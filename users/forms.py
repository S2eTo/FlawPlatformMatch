from django import forms

from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _

from users.models import User
from common.file import get_extension


class UserCreationForm(forms.ModelForm):
    """
        A form that creates a user, with no privileges, from the given username and
        password.
        """
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }

    password1 = forms.CharField(label=_("Password"))
    password2 = forms.CharField(label=_("Password confirmation"))

    class Meta:
        model = User
        fields = ("username", )
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ImportUserForm(forms.Form):
    """
    导入用户信息表单
    """

    error_messages = {
        'file_extension': "只能上传 excel (.xls )文件",
    }
    required_css_class = 'required'
    excel_file = forms.FileField(
        label="文件",
        help_text="选择报名信息表进行导入, 导入信息时间可能比较长，请耐心等待出现完成导入提示。",
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')
        ext = get_extension(excel_file.name)

        # 判断文件后缀
        if ext not in ['xls']:
            raise ValidationError(
                self.error_messages['file_extension'],
                code='file_extension',
            )
        
        return excel_file
