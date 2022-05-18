from django.db import models
from django.core.exceptions import ValidationError


class BaseModels(models.Model):
    """
    数据库公共字段, 父类, 基类
    """
    auto_add_help_text = "创建后自动分配"

    custom_validate = False
    custom_validators = []

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='自动填写，创建时的日期与时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='最近更新', help_text='自动更新，最近一次保存的日期与时间')

    class Meta:
        abstract = True

    error_messages = {
        'unique': "该邮箱已注册！",
    }

    def is_empty_values(self, value):
        """
        判断值是否为空
        """

        return value in models.Field.empty_values or value is None

    def pre_field_clean(self, field: models.Field, raw_value):
        """
        于函数 clean_fields() 中, pre_clean_[field.name] 与 models.Field.clean 前
        """

        return raw_value

    def post_field_clean(self, field: models.Field, value):
        """
        于函数 clean_fields() 中, models.Field.clean 与 post_clean_[field.name] 后
        """

        return value

    def clean_fields(self, exclude=None):
        """
        重写 clean_fields 方法，为 models 新增自定义字段验证的方法，下列方法由上往下执行

        # 调用字段 Field.clean 调用的函数前调用，这里我特地将其写到了跳过空验证的前面
        pre_field_clean(self, field: models.Field, raw_value) -> (models.Field, Any)

        # 调用字段 Field.clean 调用的函数前调用，这里我特地将其写到了跳过空验证的前面
        pre_clean_[Field.name](self, field: models.Field, raw_value) -> (models.Field, Any)

        # 调用字段 Field.clean 调用的函数后调用
        post_clean_[Field.name](self, field: models.Field, raw_value) -> (models.Field, Any)

        # 调用字段 Field.clean 调用的函数后调用
        post_field_clean(self, field: models.Field, value) -> (models.Field, Any)
        """

        # 排除列表
        if exclude is None:
            exclude = []

        errors = {}
        for f in self._meta.fields:

            # 如果字段再排除列表中跳过字段验证
            if f.name in exclude:
                continue

            # 获取值
            raw_value = getattr(self, f.attname)

            try:
                raw_value = self.pre_field_clean(f, raw_value)

                # 增加 pre_clean_[field.name] 方法
                if hasattr(self, 'pre_clean_%s' % f.name):
                    raw_value = getattr(self, 'pre_clean_%s' % f.name)(f, raw_value)

                # 当 blank=True 时跳过验证空字段验证
                # 开发人员负责确保它们具有有效的值。
                if f.blank and raw_value in f.empty_values and f.name:
                    continue

                # 调用字段的 clean 方法, 调用 default_validators 中的验证其
                value = f.clean(raw_value, self)

                # 增加 post_clean_[field.name] 方法
                if hasattr(self, 'post_clean_%s' % f.name):
                    value = getattr(self, 'post_clean_%s' % f.name)(f, value)

                value = self.post_field_clean(f, value)

                # 设置值
                setattr(self, f.attname, value)

            except ValidationError as e:
                errors[f.name] = e.error_list

        if errors:
            raise ValidationError(errors)
