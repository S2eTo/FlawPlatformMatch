import threading

from django import forms
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.http.response import HttpResponse, HttpResponseRedirect

from dockerapi.api import docker_api
from ws.dispatcher import dispatcher
from users.models import Notice, Match
from dockerapi.models import Image, Container, Checked, Category, Hints


class ContainerCreationForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ("image",)


class ContainerChangeForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ('image', 'container_id', 'name', 'public_port', 'user')


def post_delete_selected(queryset):
    """
    后台执行批量删除动作后，删除容器
    """

    pass


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    add_form = ContainerCreationForm
    change_form = ContainerChangeForm

    autocomplete_fields = ('image',)
    list_display = ('container_id', 'public_port', 'image', 'user', 'create_time', 'update_time')
    list_filter = ('create_time', 'update_time')
    search_fields = ('container_id', 'image__image_id', 'user', 'image__name')
    list_per_page = 10

    def delete_queryset(self, request, queryset):
        """
        兼容删除动作, 删除同时将容器删除
        """

        # 删除容器
        def threading_delete():
            for container in queryset:
                container.is_delete = True
                docker_api.delete(container_id=container.container_id, job_id=container.job_id)

        threading.Thread(target=threading_delete).start()

        # 执行原生删除
        super().delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        """
        后台保存的时候, 自动填充用户名
        """

        if not change:
            obj.user = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        """
        在容器创建时，使用自定义表单
        """

        defaults = {}
        if obj is None:
            self.readonly_fields = ()
            defaults['form'] = self.add_form
        else:
            self.readonly_fields = ('image', 'container_id', 'name', 'public_port', 'user', 'create_time',
                                    'update_time')
            defaults['form'] = self.change_form

        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def has_change_permission(self, request, obj=None):
        """
        不给修改权限
        """

        return False


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    add_form_template = 'admin/image_add_form.html'
    change_form_template = 'admin/image_add_form.html'

    fieldsets = (
        ('环境选择', {'classes': ('dev',), 'fields': ('check_flag',)}),
        ('镜像环境', {'classes': ('image_dev',), 'fields': ('image_id', 'image_tags', 'expose')}),
        ('镜像 FLAG 样式', {'classes': ('flag_style',), 'fields': ('image_flag_style', 'fixed_flag',
                                                               'flag_file_path', 'flag_file_format')}),
        ('附件环境', {'classes': ('file_dev',), 'fields': ('file', 'file_flag')}),
        ('题目信息', {'classes': ('info',),
                  'fields': ('name', 'source', 'point', 'category', 'description', 'top_user', 'done_count',
                             'create_time', 'update_time')}),
    )

    list_display = ('name', 'check_flag', 'source', 'category', 'status', 'change_status_field')
    list_filter = ('check_flag', 'category', 'status', 'create_time', 'update_time')
    search_fields = ('name', 'image_id', 'description', 'source')
    # filter_horizontal = ('top_user', )
    list_per_page = 10

    def change_status_field(self, obj: Image):

        if obj.status == 0:
            return format_html('<a href="{}" class="addlink">上架题目</a>',
                               reverse('admin:release_task', kwargs={'id': obj.id}))

        return format_html('<a href="{}" class="deletelink">紧急下架题目</a>',
                           reverse('admin:off_release_task', kwargs={'id': obj.id}))

    change_status_field.short_description = "操作"

    def get_urls(self):

        return [
                   path(
                       'release/<int:id>/',
                       self.admin_site.admin_view(self.release),
                       name='release_task',
                   ),
                   path(
                       'off_release/<int:id>/',
                       self.admin_site.admin_view(self.off_release),
                       name='off_release_task',
                   ),
               ] + super(ImageAdmin, self).get_urls()

    def release(self, request, id, form_url=''):

        # 鉴权
        if not self.has_change_permission(request):
            raise PermissionDenied

        # 比赛开始才能
        match = Match.objects.first()
        if match is None:
            messages.error(request, '没有比赛！！不能上架题目。')
            return HttpResponseRedirect(redirect_to='../../')

        if not match.is_start():
            messages.error(request, '比赛尚未开始，不能发布题目.')
            return HttpResponseRedirect(redirect_to='../../')

        if request.method == 'POST' and request.POST.get('post'):

            id = int(request.POST.get('id'))

            if id in [None, '']:
                return HttpResponse(status=404)

            try:
                queryset = Image.objects.get(id=id)
            except Image.DoesNotExist:
                return HttpResponse(status=404)

            queryset.status = 1
            queryset.save()

            # 发布公告
            notice = Notice()
            notice.content = "题目 《{}》 已发布.".format(queryset.name)
            notice.save()

            # 更新题目
            dispatcher.send_all({'type': 'update_task', 'data': queryset.category.id})

            messages.success(request, "发布成功")
            return HttpResponseRedirect(redirect_to='../../')

        try:
            queryset = Image.objects.get(id=id)
        except Image.DoesNotExist:
            return HttpResponse(status=404)

        context = {
            'title': '确定要上架该题目吗？',
            'descriotion': '',
            'queryset': queryset,
            'opts': queryset._meta,
            'check_flag': ["镜像环境", "附件环境"]
        }

        # Display the confirmation page
        return TemplateResponse(request, "admin/confirmation_release.html", context)

    def off_release(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied

        if request.method == 'POST' and request.POST.get('post'):
            id = int(request.POST.get('id'))

            if id in [None, '']:
                return HttpResponse(status=404)

            try:
                queryset = Image.objects.get(id=id)
            except Image.DoesNotExist:
                return HttpResponse(status=404)

            queryset.status = 0
            queryset.save()

            # 删除停止所有相关容器
            try:
                containers = Container.objects.filter(image_id=queryset.id)
                for container in containers:
                    container.delete()

            except Exception:
                pass

            notice = Notice()
            notice.content = "题目 《{}》 已紧急下架.".format(queryset.name)
            notice.save()

            # 更新题目
            dispatcher.send_all({'type': 'update_task', 'data': queryset.category.id})

            messages.success(request, "操作成功")
            return HttpResponseRedirect(redirect_to='../../')

        try:
            queryset = Image.objects.get(id=id)
        except Image.DoesNotExist:
            return HttpResponse(status=404)

        context = {
            'title': '确定要紧急下架该题目吗？',
            'descriotion': '如果紧急下架该题目，该题目为镜像环境题目会强制关闭所有已启动容器（环境）, 这会耗费很多资源，请谨慎操作。',
            'queryset': queryset,
            'opts': queryset._meta,
            'check_flag': ["镜像环境", "附件环境"]
        }

        # Display the confirmation page
        return TemplateResponse(request, "admin/confirmation_release.html", context)

    def get_readonly_fields(self, request, obj=None):
        # if obj is None:
        #     self.readonly_fields = ()
        # else:
        self.readonly_fields = ('done_count', 'top_user', 'create_time', 'update_time')
        return self.readonly_fields


@admin.register(Checked)
class CheckedAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'create_time')
    list_filter = ('create_time',)
    search_fields = ('user_username', 'image__image_name')
    # readonly_fields = ('user', 'image')
    list_per_page = 10

    def has_add_permission(self, request):
        """
        不给后台添加权限
        """

        return False

    def has_change_permission(self, request, obj=None):
        """
        不给后台修改权限
        """

        return False

    # def has_delete_permission(self, request, obj=None):
    #     """
    #     不给后台删除权限
    #     """
    #
    #     return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('create_time', 'update_time')
    search_fields = ('name',)
    list_per_page = 10


@admin.register(Hints)
class HintsAdmin(admin.ModelAdmin):
    fields = ('content', 'image')
    list_display = ('content', 'image', 'status', 'create_time', 'update_time')
    list_editable = ('status',)
    list_filter = ('status', 'create_time', 'update_time')
    search_fields = ('content', 'image')
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            status = form.cleaned_data.get('status')
            notice = Notice()
            notice.content = f"题目 《{obj.image.name}》 {'有新提示发布' if status else '有提示被关闭'}了."
            notice.save()

        dispatcher.send_all({
            'type': 'update_task_hints', 'data': {
                "category": obj.image.category.id,
                "image": obj.image.id,
            }
        })

        super(HintsAdmin, self).save_model(request, obj, form, change)
