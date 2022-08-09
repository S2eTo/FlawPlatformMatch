import json
import uuid
import os.path
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth.models import AbstractUser

from common.models import BaseModels
from ws.dispatcher import dispatcher


class User(AbstractUser):
    point = models.IntegerField(default=0.0, verbose_name="用户积分")
    student_id = models.CharField(default=None, blank=True, max_length=200, null=True, verbose_name="学号")
    classes = models.CharField(default=None, blank=True, max_length=200, null=True, verbose_name="班级")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class EmailToken(BaseModels):
    key = models.CharField(max_length=255, verbose_name="Token")
    email = models.EmailField(verbose_name='邮箱')
    mode = models.IntegerField(choices=(
        (1, '用户注册'),
        (2, '重置密码')
    ), default=1, verbose_name="Token 类型")
    expiration = models.DateTimeField(blank=False)

    def save(self, *args, **kwargs):
        # 设置过期时间 30 分钟后
        if not self.expiration:
            self.expiration = timezone.now() + timedelta(minutes=int(settings.EMAIL_TOKEN_TIMEOUT))

        # 自动生成唯一 Token
        self.key = "{}-{}".format(datetime.now().strftime('%Y%m%d%H%M%S%f'), uuid.uuid4())
        super(EmailToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "邮箱认证 Token"
        verbose_name_plural = verbose_name

    def interval(self) -> bool:
        """
        判断 60 秒内是否已经操作
        """

        return (timezone.now() + timedelta(seconds=-60)) < self.update_time

    def is_expiration(self) -> bool:
        """
        判断是否过期
        """

        return timezone.now() > self.expiration

    @classmethod
    def remove_expired(cls):
        """
        删除已过期的 Token
        """

        cls.objects.filter(expiration__lte=timezone.now()).delete()


class Notice(BaseModels):
    content = models.TextField(verbose_name="公告内容")
    ctimer = models.CharField(max_length=200, blank=True, verbose_name="创建时间")

    def __str__(self):
        return self.content[:15] + "..."

    class Meta:
        verbose_name = "公告"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.ctimer = datetime.now().strftime('%H:%M:%S')

        # 实时推送答题动态
        dispatcher.send_all({'type': 'update_notice'})

        super(Notice, self).save(*args, **kwargs)


class Match(BaseModels):
    name = models.CharField(max_length=200, verbose_name="比赛名称")
    logo = models.ImageField(upload_to='logo/%Y/%m', verbose_name="logo")
    start_datetime = models.DateTimeField(verbose_name="开始时间")
    end_datetime = models.DateTimeField(verbose_name="结束时间")
    record_login = models.BooleanField(choices=((True, "限制比赛后登录行为"), (False, "不限制比赛后登录行为")),
                                       help_text="开启限制时, 需要选手在比赛前登录, 比赛后无法登录. 如特殊情况需要再次登录的, 可以将选手登录状态改为失效。",
                                       default=True, verbose_name="限制登录")

    class Meta:
        verbose_name = "比赛"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def is_start(self):
        """
        是否已经开始比赛
        """

        return timezone.now() > self.start_datetime

    def is_end(self):
        """
        是否已经结束比赛
        """

        return timezone.now() >= self.end_datetime

    def is_during(self):
        """
        是否在比赛期间
        """

        return self.is_start() and not self.is_end()

    def is_record_login(self):
        return self.record_login and self.is_start()


class UserToken(BaseModels):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="用户")
    ip = models.CharField(max_length=200, verbose_name="登录 IP")
    status = models.BooleanField(choices=(
        (False, "正常"),
        (True, "失效"),
    ), default=False, help_text="设置为失效后, 就可以再次登录。 不需要删除数据，以多次登录IP判断是否作弊。",
        verbose_name="状态")
    remark = models.CharField(max_length=200, verbose_name="备注")

    def __str__(self):
        return f"UserToken: {self.user}"

    def colored_name(self):
        if self.status:
            color = "#bf2b2b"
            content = "已失效"
        else:
            color = "#70bf2b"
            content = "正常"

        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            content,
        )

    colored_name.short_description = "状态"

    class Meta:
        verbose_name = "选手登录状态"
        verbose_name_plural = verbose_name
