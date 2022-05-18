from captcha.fields import CaptchaStore

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from users.models import EmailToken


class GetImagesValidation(forms.Form):
    category = forms.IntegerField(label="类型", min_value=0, required=True, error_messages={
        'invalid': "类型参数是整数哟.",
    })


class IdValidation(forms.Form):
    id = forms.IntegerField(label="id", min_value=1, required=True, error_messages={
        'required': 'ID 不能为空!'
    })


class FlagValidation(forms.Form):
    image_id = forms.IntegerField(label="题目 ID", min_value=1, required=True, error_messages={
        'required': '题目 ID 不能为空!',
    })
    flag = forms.CharField(label='flag', max_length=255, required=True, error_messages={
        'required': 'flag 不能为空！',
    })


class EmailTokenValidation(forms.Form):
    error_messages = {
        'expire': '注册链接已过期，请重新获取'
    }

    key = forms.CharField(max_length=255, label="激活码", error_messages={
        'required': '激活码不能为空',
    })

    def clean_key(self):
        try:
            # step1: 在数据库中获取激活码记录
            key = self.cleaned_data.get('key')
            email_token = EmailToken.objects.get(key=key)

            # step2: 判断是否过期
            if email_token.is_expiration():
                # 删除 Token
                email_token.delete()

                raise ValidationError(
                    self.error_messages['expire'],
                    code='expire',
                )

        except EmailToken.DoesNotExist:
            raise ValidationError(
                self.error_messages['expire'],
                code='expire',
            )

        return email_token


class CaptchaValidation(forms.Form):
    error_messages = {
        'incorrect': '验证码错误',
        'expire': '验证码已过期'
    }

    image_id = forms.IntegerField(label="id", min_value=1, error_messages={
        'required': '验证码 id 不能为空'
    })
    captcha_code = forms.CharField(label="验证码", error_messages={
        'required': '验证码不能为空'
    })

    def clean_captcha_code(self):
        """
        对比验证码与数据库中的验证码
        """

        image_id = self.cleaned_data.get('image_id')
        try:
            image_code = CaptchaStore.objects.get(id=image_id)

        except CaptchaStore.DoesNotExist:
            raise ValidationError(
                self.error_messages['incorrect'],
                code='incorrect',
            )

        if timezone.now() > image_code.expiration:
            raise ValidationError(
                self.error_messages['expire'],
                code='expire',
            )

        if image_code:

            captcha_code = self.cleaned_data.get('captcha_code')

            if image_code.response != captcha_code.lower():
                raise ValidationError(
                    self.error_messages['incorrect'],
                    code='incorrect',
                )

            # 验证完后删除验证码, 防止重复使用
            image_code.delete()
