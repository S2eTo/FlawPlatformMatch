from django.urls import path

from dockerapi.views import GetImage

urlpatterns = [
    path('get_image', GetImage.as_view()),

]
