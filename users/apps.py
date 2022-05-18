import os

from django.apps import AppConfig

default_app_config = 'users.UsersConfig'
VERBOSE_APP_NAME = "比赛管理"


def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name = 'users'
    name = get_current_app_name(__file__)
    verbose_name = VERBOSE_APP_NAME
