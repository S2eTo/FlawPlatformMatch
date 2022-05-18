from django.urls import path

from ws.views import (index)

urlpatterns = [
    path('', index),
]
