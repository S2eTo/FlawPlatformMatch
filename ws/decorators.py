from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware

from ws.middleware import WebSocketMiddleware

__all__ = ('accept_websocket', 'require_websocket')


def _setup_websocket(func):
    from functools import wraps
    @wraps(func)
    def new_func(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if response is None and request.is_websocket():
            response = HttpResponse()
            response.__len__ = lambda: 0
            return response
        return response

    decorator = decorator_from_middleware(WebSocketMiddleware)
    new_func = decorator(new_func)
    return new_func


def accept_websocket(func):
    func.accept_websocket = True
    func.require_websocket = getattr(func, 'require_websocket', False)
    func = _setup_websocket(func)
    return func


def require_websocket(func):
    func.accept_websocket = True
    func.require_websocket = True
    func = _setup_websocket(func)
    return func
