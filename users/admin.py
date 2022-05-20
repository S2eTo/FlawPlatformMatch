import os
import uuid
import json
import random
from datetime import datetime

import xlwt
import xlrd
import django.db.utils

from django.conf import settings
from django.utils import timezone
from django.utils.html import escape
from django.urls import path, reverse
from django.db.models import F, Window
from django.db import router, transaction
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponseRedirect
from django.contrib.admin.options import IS_POPUP_VAR
from django.db.models.functions import Rank as ORMRank
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from django.utils.translation import gettext, gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from users.forms import ImportUserForm
from users.models import User, Notice, Match, UserToken
from dockerapi.models import Image, Container, Checked, Category, Hints

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


def generate_rand_str(length: int = 8) -> str:
    """
    生成指定长度的随机字符串

    @param length: 可选，指定生成字符串长度，默认为 6
    @return:
    """
    return "".join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', length))


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'classes', 'email', 'point')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    change_list_template = "admin/user_change_list.html"
    list_display = ('username', 'first_name', 'point')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_urls(self):
        return [
                   path(
                       '<id>/password/',
                       self.admin_site.admin_view(self.user_change_password),
                       name='auth_user_password_change',
                   ),
                   path(
                       'import',
                       self.admin_site.admin_view(self.import_from_excel),
                       name='import_user_from_excel',
                   ),
                   path(
                       'clear_ordinary_user',
                       self.admin_site.admin_view(self.clear_ordinary_user),
                       name='clear_ordinary_user',
                   ),
               ] + super().get_urls()

    @sensitive_post_parameters_m
    def import_from_excel(self, request, form_url=''):
        """
        导入用户视图
        """

        # 校验是否有添加用户权限
        if not self.has_add_permission(request):
            raise PermissionDenied

        if request.method == 'POST':
            form = ImportUserForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data.get('excel_file')

                filename = "{}-{}.xls".format(datetime.now().strftime('%Y%m%d%H%M%S%f'), uuid.uuid4())
                filename = os.path.join(settings.BASE_DIR, 'excel', filename)

                os.makedirs(os.path.dirname(filename), exist_ok=True)

                f = open(filename, 'wb')
                for chunk in file.chunks():
                    f.write(chunk)
                f.close()
                # try:
                data = xlrd.open_workbook(filename, encoding_override='utf-8')
                sheet_name = data.sheet_names()[0]
                table_name = data.sheet_by_name(sheet_name)
                nrows = table_name.nrows  # 总行数

                users_info = []
                try:
                    # 利用事务执行导入
                    with transaction.atomic(using=router.db_for_write(self.model)):
                        for i in range(1, nrows):
                            sheet_row_val = table_name.row_values(i)

                            password = generate_rand_str()
                            username = int(sheet_row_val[2])

                            user1: User = User()
                            user1.set_password(password)
                            user1.username = username
                            user1.first_name = sheet_row_val[0]
                            user1.classes = sheet_row_val[1]
                            user1.save()

                            users_info.append({
                                "username": username,
                                "password": password
                            })

                except django.db.utils.IntegrityError as e:
                    form.add_error('excel_file', '位于行: {}, 存在重复的学号: {}'.format(i + 1, username))
                    users_info.clear()

                os.remove(filename)

                if form.is_valid():
                    # 用户名密码写入文件
                    f = open(os.path.join(settings.BASE_DIR, 'excel', "password.json"), 'wb')
                    f.write(json.dumps(users_info).encode())
                    f.close()

                    messages.success(request, '导入成功')

        elif request.method == "GET":
            form = ImportUserForm()

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': "批量导入 %s 信息" % self.model._meta.verbose_name,
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'is_popup_var': IS_POPUP_VAR,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/import_users_from_excel.html',
            context,
        )

    @sensitive_post_parameters_m
    def clear_ordinary_user(self, request, form_url=''):
        if request.method == 'POST' and request.POST.get('post'):
            try:
                User.objects.filter(is_superuser=False, is_staff=False).delete()

                messages.success(request, '已清空 %s' % self.model._meta.verbose_name)

                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist" % (
                            self.admin_site.name,
                            self.model._meta.app_label,
                            self.model._meta.model_name
                        )
                    )
                )

            except Exception as e:
                messages.error(request, e)

        context = {
            "title": "清空 %s" % self.model._meta.verbose_name,
            "descriotion": "此操作将会清空所有非职员/超级管理元用户, 请谨慎操作!",
            "opts": self.model._meta,
        }

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/clear_ordinary_user.html',
            context,
        )

    def lookup_allowed(self, lookup, value):
        # Don't allow lookups involving passwords.
        return not lookup.startswith('password') and super().lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    def add_view(self, request, form_url='', extra_context=None):
        with transaction.atomic(using=router.db_for_write(self.model)):
            return self._add_view(request, form_url, extra_context)

    def _add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super().add_view(request, form_url, extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST' and request.POST.get('post'):
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'is_popup_var': IS_POPUP_VAR,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    fields = ('content',)
    list_display = ('content', 'create_time', 'update_time')
    search_fields = ('content',)
    list_filter = ('create_time', 'update_time')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_datetime', 'end_datetime')
    search_fields = ('name',)
    change_list_template = "admin/match_change_list.html"
    list_filter = ('start_datetime', 'end_datetime', 'create_time', 'update_time')

    def get_urls(self):

        return [
                   path(
                       'reset',
                       self.admin_site.admin_view(self.reset),
                       name='reset_match',
                   ),
                   path(
                       'export',
                       self.admin_site.admin_view(self.export_achievement),
                       name='export_achievement',
                   ),
               ] + super(MatchAdmin, self).get_urls()

    @sensitive_post_parameters_m
    def export_achievement(self, request, form_url=''):
        # 表头
        theader = ['排名', '名字', '学号', '班级']

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('比赛结果')

        # 获取排行榜
        rank_result = User.objects.exclude(is_superuser=True).annotate(
            rank=Window(
                expression=ORMRank(),
                order_by=F("point").desc()
            )
        ).values("id", "username", "first_name", "is_superuser", 'student_id', "point", "classes", "rank")

        categorys = []
        for item in Category.objects.all():
            theader.append(f"{item.name} 完成度")
            categorys.append({
                "name": item.name,
                "count": Image.objects.filter(category=item).count()
            })

        theader.append("分数")

        # 写入表头
        for i in range(0, len(theader)):
            worksheet.write(0, i, theader[i])

        i = 1
        rank_list = []
        for user in rank_result:
            worksheet.write(i, 0, user['rank'])
            worksheet.write(i, 1, user['first_name'] if user['first_name'] else user['username'])
            worksheet.write(i, 2, user['student_id'])
            worksheet.write(i, 3, user['classes'])

            # 计算完成度
            n = 4
            for category in categorys:
                if category["count"] == 0:
                    worksheet.write(i, n, '0%')
                else:
                    c = Checked.objects.filter(user_id=user["id"], image__category__name=category["name"]).count()
                    p = round(c / category["count"], 2)

                    worksheet.write(i, n, f'{p if int(p) != 0 else "0"}%')
                n += 1

            worksheet.write(i, n, user['point'])
            # 计算完成率

        now = timezone.now()
        filename = os.path.join(settings.BASE_DIR, 'media')
        filename = os.path.join(filename, 'export')
        filename = os.path.join(filename, str(now.month))
        filename = os.path.join(filename, str(now.day))
        filename = os.path.join(filename, "比赛结果.xls")

        # 创建目录
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        workbook.save(filename)

        return HttpResponseRedirect(redirect_to='/media/export/{}/{}/比赛结果.xls'.format(str(now.month), str(now.day)))

    @sensitive_post_parameters_m
    def reset(self, request, form_url=''):
        if request.method == 'POST' and request.POST.get('post'):
            with transaction.atomic(using=router.db_for_write(self.model)):
                users = User.objects.all()
                users.update(**{"point": 0})

                # 关闭所有提示
                Hints.objects.all().update(status=False)

                # 删除所有答题记录
                Checked.objects.all().delete()

                # 删除所有公告
                Notice.objects.all().delete()

                # 删除所有 Token
                UserToken.objects.all().delete()

                # 删除所有容器
                Container.objects.all().delete()

                for image in Image.objects.all():
                    image.point = 1000
                    image.top_user.clear()
                    image.status = 0
                    image.done_count = 0
                    image.save()

            messages.success(request, '重置成功！')

            return HttpResponseRedirect(
                reverse(
                    "%s:%s_%s_changelist" % (
                        self.admin_site.name,
                        Match._meta.app_label,
                        Match._meta.model_name
                    )
                )
            )

        context = {
            'title': '确定要重置比赛吗？',
            'descriotion': '所有数据将会回到初始状态',
            'opts': Match._meta,
        }

        # Display the confirmation page
        return TemplateResponse(request, "admin/confirmation_reset.html", context)


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'ip', 'status', 'create_time', 'update_time')
    list_editable = ('status', )
    readonly_fields = ('user', 'token', 'create_time', 'update_time', 'colored_name', 'ip')
    search_fields = ('user__username', )
    list_filter = ('create_time', 'update_time')

    fields = ('user', 'token', 'colored_name', 'ip', 'create_time', 'update_time')

    def has_add_permission(self, request):
        return False


# @admin.register(UserRequestHistory)
# class UserRequestHistoryAdmin(admin.ModelAdmin):
#     list_display = ('user', 'ip', 'full_path','create_time', 'update_time')
#     search_fields = ('user__username',)
#     list_filter = ('create_time', 'update_time')
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         return False

