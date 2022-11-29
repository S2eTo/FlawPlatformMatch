import base64

from captcha.views import (
    CaptchaStore, captcha_image
)
from django.conf import settings
from django.db.models.functions import Rank as ORMRank
from django.db.models import F, Window
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm

from ws.dispatcher import dispatcher
from common.decorators import validate
from common.calculator import Calculator
from dockerapi.models import (
    Image, Container, Checked, Category
)
from users.models import (
    User, EmailToken, Notice, Match, UserToken
)
from common.views import (
    UserAPIView, AnonymousAPIView, AdministratorAPIView, CheckGetPermissionsAPIView, CheckPostPermissionsAPIView
)
from v1.validators import (
    IdValidation, GetImagesValidation, FlagValidation, EmailTokenValidation, CaptchaValidation,
)
from v1.serializers import (
    ImagesSerializer, ContainerSerializer, CheckedSerializer, UserSerializer, CategorySerializer, NoticeSerializer,
    UserCheckedSerializer, MatchSerializer
)


class GetCaptcha(AnonymousAPIView):
    """
    获取验证码
    """

    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        try:
            # 获取图片id
            id_ = CaptchaStore.objects.filter(hashkey=hashkey).first().id
            image = captcha_image(request, hashkey)
            # 将图片转换为base64
            image_base = 'data:image/png;base64,%s' % base64.b64encode(image.content).decode('utf-8')
            json_data = {
                "id": id_,
                "image_base": image_base
            }

            # 批量删除过期验证码
            CaptchaStore.remove_expired()
        except Exception:
            json_data = None

        return self.success('获取成功', data=json_data)


class Login(AnonymousAPIView):
    """
    用户登录
    """

    @validate(validator=(CaptchaValidation, AuthenticationForm))
    def post(self, request, data: AuthenticationForm):

        match = Match.objects.first()

        if match is not None:
            # 查找用户是否已经登录过
            user: User = data.get_user()
            # 是否需要记录
            if match.is_record_login() and not user.is_superuser:
                try:
                    UserToken.objects.get(user=user, status=False)
                    return self.failed('登陆失败, 重复登录了！！！！！')
                except UserToken.DoesNotExist:
                    pass

        login(request, user=data.get_user())

        if request.user:

            if not request.user.is_superuser:

                # 记录来源地址
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = list()

                if x_forwarded_for:
                    ip.extend(x_forwarded_for.split(','))

                ip.append(request.META.get('REMOTE_ADDR'))

                # 登录后生成 Token
                user_token = UserToken()
                if match.is_start():
                    user_token.remark = "比赛开始后登录"
                else:
                    user_token.remark = "比赛开始前登录"

                user_token.user = request.user
                user_token.ip = ", ".join(ip)
                user_token.save()

            return self.success('登陆成功', data={
                'token': request.session.session_key,
                'user': UserSerializer(request.user).data
            })

        return self.failed('登陆失败, 是不是忘记报名了呢！')


class Logout(UserAPIView, CheckPostPermissionsAPIView):
    """
    退出登录
    """

    def post(self, request):
        logout(request)
        return self.success('退出登录成功。')


class CheckIn(UserAPIView, CheckPostPermissionsAPIView):
    """
    检查是否已登录
    """

    def post(self, request):
        return self.success('登陆成功', data=UserSerializer(request.user).data)


class GetUserInfo(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取用户信息
    """

    def get(self, request):
        return self.success('获取成功', data={'user': UserSerializer(request.user).data})


class ResetPassword(AnonymousAPIView):

    @validate(validator=(CaptchaValidation, EmailTokenValidation))
    def post(self, request, data: EmailTokenValidation):
        # step1: 获取注册码对象
        email_token: EmailToken = data.cleaned_data.get('key')

        # step2: 判断验证码类型
        if email_token.mode != 2:
            return self.failed('注册链接已过期，请重新获取')

        # step3: 获取用户
        try:
            user = User.objects.get(email=email_token.email)
        except User.DoesNotExist:
            return self.failed('注册链接已过期，请重新获取')

        # step4: 重置密码
        admin_password_change_form = AdminPasswordChangeForm(user=user, data=request.POST)
        if admin_password_change_form.is_valid():
            admin_password_change_form.save()
        else:
            return self.failed('请求失败!', data={'errors': admin_password_change_form.errors, 'form_errors': True})

        return self.success('密码重置成功！')


class GetImages(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取题目列表
    """

    @validate(GetImagesValidation)
    def get(self, request, data: GetImagesValidation):
        data = Image.objects.filter(category_id=data.cleaned_data.get('category'), status=1)

        return self.success('获取成功', data=ImagesSerializer(data, many=True).data)


class GetImage(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取题目详细
    """

    @validate(IdValidation)
    def get(self, request, data: IdValidation):
        try:
            data = Image.objects.get(id=data.cleaned_data.get('id'), status=1)
        except Image.DoesNotExist:
            return self.failed(msg="题目不存在", status=400)

        return self.success(msg="获取成功", data=ImagesSerializer(data).data)


class RunContainer(UserAPIView, CheckPostPermissionsAPIView):
    """
    启动环境
    """

    @validate(IdValidation)
    def post(self, request, data: IdValidation):

        # 检查是否已经开启了容器
        try:
            container = Container.objects.get(user=request.user)
            return self.success('题目 《{}》 已存在启动容器！'.format(container.image.name),
                                data={'container': ContainerSerializer(container).data,
                                      'remaining_time': settings.DOCKER_API.get('AUTO_REMOVE_CONTAINER')}, code=2)
        except Container.DoesNotExist:
            pass

        try:
            image = Image.objects.get(id=data.cleaned_data.get('id'), status=1)
        except Image.DoesNotExist:
            return self.failed(msg="题目不存在", status=400)

        container = Container()
        container.image = image
        container.user = request.user
        container.save()

        return self.success("启动成功！", data={
            'container': ContainerSerializer(container).data,
            'remaining_time': settings.DOCKER_API.get('AUTO_REMOVE_CONTAINER')
        })


class GetRunningContainer(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取用户运行中的容器
    """

    def get(self, request):
        try:
            container = Container.objects.get(user=request.user)
            return self.success('获取成功', data={
                'container': ContainerSerializer(container).data,
                'remaining_time': settings.DOCKER_API.get('AUTO_REMOVE_CONTAINER')
            })

        except Container.DoesNotExist:
            return self.success('获取成功', data={'container': None})


class RemoveContainer(UserAPIView, CheckPostPermissionsAPIView):

    def post(self, request):

        try:
            container = Container.objects.get(user=request.user)

            container.delete()

            return self.success('已成功删除环境')
        except Container.DoesNotExist:
            return self.failed('关闭失败，未找到相应容器', data={'container': None}, code=2)


class CheckFlag(UserAPIView, CheckPostPermissionsAPIView):
    """
    提交 flag
    """

    @validate(FlagValidation)
    def post(self, request, data: FlagValidation):

        # 比赛结束后无法提交flag
        match = Match.objects.first()
        if match.is_end():
            return self.failed(msg="比赛已结束", status=400)

        try:
            # 获得当前题目
            task = Image.objects.get(id=data.cleaned_data.get('image_id'), status=1)
        except Image.DoesNotExist:
            return self.failed(msg="题目不存在", status=400)

        try:
            # 判断这题是否已经回答过了
            checked = Checked.objects.get(user=request.user, image=task)
            if checked:
                return self.failed('已经回答过啦！进入下一题吧。')
        except Checked.DoesNotExist:
            pass

        # 确定检查方式
        if task.check_flag == 1:
            try:
                container = Container.objects.get(image_id=task.id, user=request.user)
            except Container.DoesNotExist:
                return self.failed('请先启动环境！', status=400)

            if task.image_flag_style == 3:
                if data.cleaned_data.get('flag') != task.fixed_flag:
                    return self.failed('对不起，你提交的 Flag 不正确。')

            else:
                if data.cleaned_data.get('flag') != container.flag:
                    return self.failed('对不起，你提交的 Flag 不正确。')

        elif task.check_flag == 2:
            if data.cleaned_data.get('flag') != task.file_flag:
                return self.failed('对不起，你提交的 Flag 不正确。')

        else:
            return self.failed('对不起，你提交的 Flag 不正确。')

        # 原始分数
        old_point = task.point
        # 当前完成人数
        count = task.done_count
        # 计算题目新分数
        new_point = Calculator.curve(old_point, count)

        # 将任务添加至答题记录代表已完成
        new_checked = Checked()
        new_checked.user = request.user
        new_checked.image = task
        new_checked.save()

        # 给用户加分
        request.user.point += Calculator.get_increment_point(new_point, count)
        request.user.save()

        # 更新题目分数
        task.point = new_point

        # 更新题目信息
        if task.done_count <= 2:
            task.top_user.add(request.user)

        task.done_count += 1

        task.save()

        # 更新计算用户手上的分数
        # step 1: 获取当前题目所有答题记录
        index = 0
        for checked in Checked.objects.filter(image=task).exclude(user=request.user):
            # step 2: 更新用户手上分数
            checked.user.point -= Calculator.get_delta_point_for_user(old_point, new_point, index)
            checked.user.save()
            index += 1

        # 实时推送更新答题动态
        dispatcher.send_all({'type': 'update_dynamic'})

        # 实时推送更新排行榜
        dispatcher.send_all({'type': 'update_rank'})

        # 实时推送更新题目信息
        dispatcher.send_all({'type': 'update_task', 'data': task.category.id})

        return self.success('恭喜你答对了！')


class GetChecked(UserAPIView, CheckGetPermissionsAPIView):
    """
    分页获取用户答题记录
    """

    def get(self, request):
        data = Checked.objects.all().exclude(user__is_superuser=True).order_by('-id')[:20]
        return self.success('获取成功', data=CheckedSerializer(data, many=True).data)


class GetAllChecked(UserAPIView, CheckGetPermissionsAPIView):
    """
    用户所有答题记录
    """

    def get(self, request):
        checked = Checked.objects.exclude(user__is_superuser=True).filter(user=request.user)

        return self.success('获取成功', data={'checked': UserCheckedSerializer(checked, many=True).data})


class RankList(UserAPIView, CheckGetPermissionsAPIView):
    """
    排名列表
    """

    def get(self, request):
        data = User.objects.exclude(is_superuser=True).annotate(
            rank=Window(
                expression=ORMRank(),
                order_by=F("point").desc()
            )
        ).values("id", "username", "first_name", "is_superuser", "point", "rank")
        return self.success('获取成功', data=data)


class CategoryList(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取分类
    """

    def get(self, request):
        data = Category.objects.all()
        return self.success('获取成功', data=CategorySerializer(data, many=True).data)


class NoticeList(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取通知
    """

    def get(self, request):
        data = Notice.objects.all().order_by('-id')
        return self.success('获取成功', data=NoticeSerializer(data, many=True).data)


class GetMatch(UserAPIView, CheckGetPermissionsAPIView):
    """
    获取比赛信息
    """

    def get(self, request):
        data = Match.objects.first()
        return self.success('获取成功', data=MatchSerializer(data).data)


class RankDetailed(AdministratorAPIView, CheckGetPermissionsAPIView):
    """
    排行详细
    """

    def get(self, request):
        # 获取排名
        rank_result = User.objects.exclude(is_superuser=True).annotate(
            rank=Window(
                expression=ORMRank(),
                order_by=F("point").desc()
            )
        )[:5].values("id", "username", "point", "first_name", "rank", 'classes')

        rank_list = []
        for rank_item in rank_result:
            # 相应队伍答题记录
            checked_queryset = Checked.objects.filter(user_id=rank_item['id'])

            rank_list.append({
                'id': rank_item['id'],
                'username': rank_item['username'],
                'first_name': rank_item['first_name'],
                'classes': rank_item['classes'],
                'point': rank_item['point'],
                'rank': rank_item['rank'],
                'checked': CheckedSerializer(checked_queryset, many=True).data
            })

        return self.success('获取成功', data=rank_list)


class CountImage(AdministratorAPIView, CheckGetPermissionsAPIView):

    def get(self, request):
        # 获取分类
        category_queryset = Category.objects.all()

        data = []
        for category in category_queryset:
            data.append({
                "id": category.id,
                "name": category.name,
                "count": Image.objects.filter(category=category).count()
            })

        return self.success('获取成功', data=data)
