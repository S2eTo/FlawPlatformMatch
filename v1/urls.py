from django.urls import path

from v1.views import (
    Login, GetImages, CheckIn, GetImage, RunContainer, GetRunningContainer, RemoveContainer,
    CheckFlag, GetUserInfo, GetChecked, GetAllChecked, GetCaptcha, Logout, ResetPassword, RankList, CategoryList,
    NoticeList, GetMatch, RankDetailed, CountImage
)


urlpatterns = [
    # 获取验证码: /v1/get_captcha
    path('get_captcha', GetCaptcha.as_view()),

    # 登录: /v1/login
    path('login', Login.as_view()),

    # 验证登录: /v1/checkin
    path('checkin', CheckIn.as_view()),

    # 退出登录: /v1/logout
    path('logout', Logout.as_view()),

    # 获取用户信息: /v1/get_userinfo
    path('get_userinfo', GetUserInfo.as_view()),

    # 重置密码: /v1/reset_password
    path('reset_password', ResetPassword.as_view()),

    # 获取题目: /v1/get_image
    path('get_image', GetImages.as_view()),

    # 获取题目详细: /v1/get_image_detail
    path('get_image_detail', GetImage.as_view()),

    # 启动容器: /v1/run_container
    path('run_container', RunContainer.as_view()),

    # 获取当前用户运行的容器: /v1/get_running_container
    path('get_running_container', GetRunningContainer.as_view()),

    # 停止并删除容器: /v1/remove_container
    path('remove_container', RemoveContainer.as_view()),

    # 提交 flag: /v1/check_flag
    path('check_flag', CheckFlag.as_view()),

    # 获取所有答题记录: /v1/get_all_checked
    path('get_all_checked', GetAllChecked.as_view()),

    # 分页获取答题记录: /v1/get_checked
    path('get_checked', GetChecked.as_view()),

    # 获取队伍排名排名：/v1/rank
    path('rank', RankList.as_view()),

    # 获取队伍排名：/v1/rank_detailed
    path('rank_detailed', RankDetailed.as_view()),

    # 获取队伍排名详细：/v1/category
    path('category', CategoryList.as_view()),

    # 获取公告：/v1/notice
    path('notice', NoticeList.as_view()),

    # 获取比赛信息：/v1/match
    path('match', GetMatch.as_view()),

    # 获取每个分类题目的数量：/v1/count_image
    path('count_image', CountImage.as_view()),

]

