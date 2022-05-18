import os

from django.apps import AppConfig

default_app_config = 'dockerapi.DockerapiConfig'
VERBOSE_APP_NAME = "题目管理"


def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]


class DockerapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name = 'dockerapi'
    name = get_current_app_name(__file__)
    verbose_name = VERBOSE_APP_NAME
