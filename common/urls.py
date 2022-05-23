"""common URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from django.shortcuts import render
from django.urls import path, include, re_path


def index(request):
    return render(request, 'index.html')


urlpatterns = [
    path('', index),

    path('admin/', admin.site.urls),

    path('v1/', include('v1.urls')),

    path('docker/', include('dockerapi.urls')),

    path('captcha', include('captcha.urls')),

    path('ws/', include('ws.urls')),

    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}, name='media'),

    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]
