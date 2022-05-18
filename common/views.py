from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdministratorUser


class BaseAPIView(APIView):
    def success(self, msg, code=1, data=None, status=200):
        if data is None:
            data = {}

        return Response({"msg": msg, "data": data, "code": code}, status=status)

    def failed(self, msg, code=0, data=None, status=400):
        if data is None:
            data = {}

        return Response({"msg": msg, "data": data, "code": code}, status=status)


class CheckPostPermissionsAPIView(BaseAPIView):

    def check_permissions(self, request):
        if request.method == "POST":
            super().check_permissions(request)


class CheckGetPermissionsAPIView(BaseAPIView):

    def check_permissions(self, request):
        if request.method == "GET":
            super().check_permissions(request)


class UserAPIView(BaseAPIView):
    """
    用户视图
    """

    # 设置判断权限：登录用户
    permission_classes = (IsAuthenticated,)


class AnonymousAPIView(BaseAPIView):
    """
    匿名视图
    """

    # 设置判断权限：允许所有
    # permission_classes = (AllowAny, )

    def check_permissions(self, request):
        pass


class AdministratorAPIView(BaseAPIView):
    """
    超级管理员视图
    """

    check_permissions_methods = (IsAdministratorUser,)
