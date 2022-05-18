import re

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.middleware import SessionMiddleware


class CorsHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """
        处理跨域响应头
        """

        response['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS'
        response['Access-Control-Max-Age'] = 'POST,GET,OPTIONS'
        response['Access-Control-Allow-Headers'] = 'content-type,x-token'
        response['Access-Control-Allow-Origin'] = '*'
        return response


class RestFulSessionMiddleware(SessionMiddleware):
    """
    前后端分离重写 Django 默认身份验证
    """

    def process_request(self, request):
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        # 如果 cookie 中没有 sessionid
        if session_key is None:
            # 如请求头中传入的参数为：X-Token 实际上会被转成 HTTP_X_TOKEN
            session_key = request.META.get("HTTP_X_TOKEN")

            request.session = self.SessionStore(session_key)


class RestFulCsrfViewMiddleware(MiddlewareMixin):
    """
    API 不设 CSRF 校验
    """

    def process_request(self, request):
        full_path = request.get_full_path()
        if re.match(r'^/v1/.*', full_path, flags=0):
            setattr(request, '_dont_enforce_csrf_checks', True)


# class UserRequestMiddleware(MiddlewareMixin):
#     """
#     记录用户访问的 IP
#
#     """
#
#     def process_request(self, request):
#         if request.user.is_authenticated and not request.user.is_superuser:
#             full_path = request.get_full_path()
#
#             if not re.match(r'(\.js|\.css|\.png|\.jpg|\.ttf|\.woff|\.map)$', full_path, flags=0) and not re.match(
#                     r'^/$', full_path, flags=0) and not re.match(r'^/static/', full_path, flags=0):
#
#                 x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#                 if x_forwarded_for:
#                     ip = x_forwarded_for.split(',')[0]
#                 else:
#                     ip = request.META.get('REMOTE_ADDR')
#
#                 history = UserRequestHistory()
#                 history.ip = ip
#                 history.full_path = full_path
#                 history.user = request.user
#                 history.save()
