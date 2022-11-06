import os
import uuid
import threading
from datetime import datetime

from django.db import models
from django.conf import settings
from docker.errors import APIError
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.exceptions import ValidationError

from common.models import BaseModels
from dockerapi.api import docker_api
from common.file import get_extension
from users.models import User, Notice


class Image(BaseModels):
    custom_validate = True

    image_id_help_text = "填写 docker images 显示的镜像ID(IMAGE ID)值, 输入完成后自动检查ID, 并显示标签(名称)及开放端口"

    check_flag = models.IntegerField(choices=(
        (1, "镜像环境"),
        (2, "附件环境")
    ), verbose_name="题目环境", default=1, help_text="指定当前题目环境")
    image_id = models.CharField(max_length=128, verbose_name="镜像 ID", help_text=image_id_help_text, blank=True,
                                null=True)
    image_tags = models.CharField(max_length=300, verbose_name="镜像标签(名称)", blank=True, null=True,
                                  help_text="自动根据镜像信息填充")
    expose = models.TextField(verbose_name="开放端口", null=True, blank=True, help_text="自动根据镜像信息填充")
    image_flag_style = models.IntegerField(choices=(
        (1, "环境变量随机flag"),
        (2, "本地文件随机flag"),
        (3, "固定 Flag")
    ), verbose_name="flag 形式", null=True, blank=True, default=1, help_text="指定镜像环境flag形式")
    fixed_flag = models.CharField(max_length=255, blank=True, null=True, verbose_name="固定 flag",
                                  help_text="无法使用随机 Flag 时, 可以提前准备好固定 Flag 后在这里设置。")
    flag_file_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="文件路径",
                                      help_text="程序会自动将随机生成flag，写入到填写的文件路径中。")
    flag_file_format = models.TextField(verbose_name="文件内容模板", blank=True, null=True, default="{FLAG}",
                                        help_text="文件内容的模板 ’{FLAG}‘ 为替换 flag 的位置。")
    file = models.FileField(upload_to="image_file/%Y/%m", blank=True, null=True, verbose_name="附件")
    file_flag = models.CharField(max_length=255, blank=True, null=True, verbose_name="附件 flag",
                                 help_text="指定附件中的flag值，用于校验（不会影响附件中的flag，所以需要提前在附件中准备flag）。")
    name = models.CharField(max_length=128, verbose_name="题目名称")
    source = models.CharField(max_length=128, default="暂无", verbose_name="题目来源")
    description = models.TextField(default="暂无", verbose_name="题目描述")
    point = models.IntegerField(verbose_name="题目分数")
    status = models.IntegerField(choices=(
        (0, "下架"),
        (1, "发布"),
    ), default=0, verbose_name="题目状态")
    category = models.ForeignKey(to="Category", on_delete=models.CASCADE, verbose_name="题目类型")
    done_count = models.IntegerField(default=0, verbose_name="完成队伍")
    top_user = models.ManyToManyField(to=User, blank=True, verbose_name="TOP 3")

    class Meta:
        verbose_name = "题目"
        verbose_name_plural = verbose_name

    error_messages = {
        'invalid': '为了避免安全问题，请将英文单引号(\')和双引号(")替换使用中文的引号(’，”)',
    }

    def pre_clean_fixed_flag(self, field: models.Field, value: str):
        if self.check_flag == 1:
            if self.image_flag_style == 3:
                if self.is_empty_values(value):
                    raise ValidationError(
                        field.error_messages['blank'],
                        code='blank',
                    )

        return value

    def pre_clean_flag_file_path(self, field: models.Field, value: str):
        if self.check_flag == 1:
            if self.image_flag_style == 2:
                if self.is_empty_values(value):
                    raise ValidationError(
                        field.error_messages['blank'],
                        code='blank',
                    )

                if value.find("'") != -1 or value.find('"') != -1:
                    raise ValidationError(
                        self.error_messages['invalid'],
                        code='invalid',
                    )

        return value

    def pre_clean_flag_file_format(self, field: models.Field, value: str):
        if self.check_flag == 1:
            if self.image_flag_style == 2:
                if self.is_empty_values(value):
                    raise ValidationError(
                        field.error_messages['blank'],
                        code='blank',
                    )

        return value

    def pre_clean_image_id(self, field: models.Field, value: str):
        if self.check_flag == 1 and self.is_empty_values(value):
            raise ValidationError(
                field.error_messages['blank'],
                code='blank',
            )

        return value

    def pre_clean_image_tags(self, field: models.Field, value: str):
        if self.check_flag == 1 and self.is_empty_values(value):
            raise ValidationError(
                field.error_messages['blank'],
                code='blank',
            )

        return value

    def pre_clean_expose(self, field: models.Field, value: str):
        if self.check_flag == 1 and self.is_empty_values(value):
            raise ValidationError(
                field.error_messages['blank'],
                code='blank',
            )

        return value

    def pre_clean_image_flag_style(self, field: models.Field, value: str):
        if self.check_flag == 1 and self.is_empty_values(value):
            raise ValidationError(
                field.error_messages['blank'],
                code='blank',
            )

        return value

    def pre_clean_file(self, field: models.Field, value: str):
        if self.check_flag == 2 and self.is_empty_values(value):
            raise ValidationError(
                field.error_messages['blank'],
                code='blank',
            )

        return value

    def pre_clean_file_flag(self, field: models.Field, value: str):
        if self.check_flag == 2 and self.is_empty_values(value):
            raise ValidationError(
                field.error_messages['blank'],
                code='blank',
            )

        return value

    def __str__(self):
        return "{}".format(self.name)

    def save(self, *args, **kwargs):
        if self.id is None:
            # 随机生成文件名防止文件名重复！
            if self.check_flag == 2 and self.file:
                self.file.name = "{}-{}.{}".format(datetime.now().strftime('%Y%m%d%H%M%S%f'), uuid.uuid4(),
                                                   get_extension(self.file.name))

            if self.flag_file_format != '{}' and not len(self.flag_file_format.strip()) > 0 and self.check_flag == 1 \
                    and self.image_flag_style == 2:
                self.flag_file_format = '{}'

        super(Image, self).save(*args, **kwargs)


class Category(BaseModels):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="名称",
        error_messages={
            'unique': "已经存在同分类了！",
        },
        help_text='队伍名称，最大长度 150 个字符',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name


class Container(BaseModels):
    error_messages = {
        'image_dev_error': "题目环境错误！附件无法启动环境！",
    }

    is_delete = False
    image_help_text = "保存后制动启动响应题目(镜像)的环境, 保存后无法修改数据。"

    container_id = models.CharField(max_length=128, null=True, verbose_name="容器 ID",
                                    help_text=BaseModels.auto_add_help_text)
    name = models.CharField(max_length=128, null=True, verbose_name="容器名称")
    public_port = models.TextField(verbose_name="开放端口", null=True)
    image = models.ForeignKey(to=Image, on_delete=models.CASCADE, null=True, verbose_name="题目(镜像)")
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, verbose_name="创建用户")
    job_id = models.CharField(max_length=128, null=True, verbose_name="定时任务 ID")
    flag = models.CharField(max_length=255, verbose_name="flag")

    def __str__(self):
        return "{} :: {}({})".format(self.user.username, self.container_id, self.name)

    class Meta:
        verbose_name = "靶机(容器)"
        verbose_name_plural = verbose_name

    def pre_clean_image(self, field: models.Field, value):

        # 如果题目类型是文件环境, 无法开启环境
        if self.image.check_flag == 2:
            raise ValidationError(self.error_messages['image_dev_error'], code='image_dev_error')

        return value

    def save(self, *args, **kwargs):
        """
        重写保存方法, 添加数据的同时启动服务器, 并启动计时任务, 无法通过后台修改数据
        """

        if self.id is None:
            self.flag = "flag{dcj%spyy}" % (uuid.uuid4(),)

            # 启动 Docker 镜像, 创建容器
            container = docker_api.run_container(self.image.image_id, self.image.expose, self.flag,
                                                 self.image.image_flag_style, self.image.flag_file_path,
                                                 self.image.flag_file_format)

            self.container_id = container.short_id
            self.name = container.name
            self.public_port = container.public_port

            # 启动定时任务, 一小时后删除容器
            job = docker_api.create_scheduler(container=self)
            self.job_id = job.id

            super(Container, self).save(*args, *kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        重写删除方法
        """

        if not self.is_delete:
            # 删除定时任务与容器
            threading.Thread(target=docker_api.delete, args=(self.container_id, self.job_id)).start()
            self.is_delete = not self.is_delete

        # 删除数据
        super(Container, self).delete(using, keep_parents)


class Checked(BaseModels):
    """
    答题记录表
    """

    image = models.ForeignKey(to=Image, on_delete=models.CASCADE, verbose_name="题目")
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="用户")
    ctimer = models.CharField(max_length=200, blank=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "答题记录"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.ctimer = datetime.now().strftime('%H:%M:%S')

        super(Checked, self).save(*args, **kwargs)


class Hints(BaseModels):
    content = models.CharField(max_length=200, blank=True, help_text="提示内容，最长 200 个字符", verbose_name="提示")
    status = models.BooleanField(choices=(
        (False, "未发布"),
        (True, "发布"),
    ), default=False, verbose_name="状态")
    image = models.ForeignKey(to=Image, on_delete=models.CASCADE, verbose_name="题目")

    class Meta:
        verbose_name = "题目 Hints"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.image.name} 题目 Hints {self.id}"


def delete_container(container_id, job_id):
    """
    直接删除镜像(题目) 后删除响应的容器
    """

    # 删除定时任务与容器
    try:
        docker_api.delete(container_id=container_id, job_id=job_id)
    except APIError:
        pass


@receiver(post_delete, sender=Container)
def custom_post_delete(sender, instance, **kwargs):
    """
    直接删除镜像(题目) 后删除响应的容器
    """

    if instance.is_delete:
        return

    threading.Thread(target=delete_container, args=(instance.container_id, instance.job_id)).start()


@receiver(post_delete, sender=Image)
def custom_post_delete(sender, instance: Image, **kwargs):
    """
    删除题目后，如果是有附件，将附件删除
    """

    if instance.check_flag == 2:

        fname = os.path.join(settings.MEDIA_ROOT, str(instance.file))
        if os.path.isfile(fname):
            os.remove(fname)
