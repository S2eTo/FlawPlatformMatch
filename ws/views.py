from django.shortcuts import render

from ws.decorators import accept_websocket
from ws.dispatcher import dispatcher


@accept_websocket
def index(request):
    # 判断 Websocket 连接
    if not request.is_websocket():
        return render(request, 'index.html')

    else:

        # Keep 住 Websocket 连接
        for message in request.websocket:
            if message:
                # 不进行任何处理
                pass

