import logging
import importlib
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from ws.dispatcher import dispatcher

WEBSOCKET_ACCEPT_ALL = getattr(settings, 'WEBSOCKET_ACCEPT_ALL', False)
WEBSOCKET_FACTORY_CLASS = getattr(
    settings,
    'WEBSOCKET_FACTORY_CLASS',
    'ws.backends.default.factory.WebSocketFactory',
)

logger = logging.getLogger(__name__)


class WebSocketMiddleware(MiddlewareMixin):

    def process_request(self, request):

        # 校验是否已经登录，只支持 Cookie
        if not request.user.is_authenticated:
            request.websocket = None
            request.is_websocket = lambda: False
            return HttpResponseForbidden()

        try:
            offset = WEBSOCKET_FACTORY_CLASS.rindex(".")

            factory_self = getattr(
                importlib.import_module(WEBSOCKET_FACTORY_CLASS[:offset]),
                WEBSOCKET_FACTORY_CLASS[offset + 1:]
            )

            # 初始化创建长连接对象
            websocket = factory_self(request).create_websocket()
            request.websocket = websocket

            # 缓存连接对象
            if websocket is not None:
                dispatcher.set(request.user, websocket)

        except ValueError as e:
            logger.debug(e)
            request.websocket = None
            request.is_websocket = lambda: False
            return HttpResponseBadRequest()
        if request.websocket is None:
            request.is_websocket = lambda: False
        else:
            request.is_websocket = lambda: True

    def process_view(self, request, view_func, view_args, view_kwargs):
        # open websocket if its an accepted request
        if request.is_websocket():
            # deny websocket request if view can't handle websocket
            if not WEBSOCKET_ACCEPT_ALL and \
                    not getattr(view_func, 'accept_websocket', False):
                return HttpResponseBadRequest()
            # everything is fine .. so prepare connection by sending handshake
            request.websocket.accept_connection()
        elif getattr(view_func, 'require_websocket', False):
            # websocket was required but not provided
            return HttpResponseBadRequest()

    def process_response(self, request, response):
        if request.is_websocket():
            request.websocket.close()

            # 删除相应缓存
            dispatcher.delete(request.user)
        return response

    def process_exception(self, request, exception):
        request.websocket.close()

        # 删除相应缓存
        dispatcher.delete(request.user)
