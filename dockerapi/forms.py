from django import forms

from dockerapi.models import Container


class ContainerCreationForm(forms.ModelForm):

    class Meta:
        model = Container
        fields = ("image", )


class ContainerChangeForm(forms.ModelForm):

    class Meta:
        model = Container
        fields = ('image', 'container_id', 'name', 'public_port', 'username', 'create_time',
                  'update_time')


# class ImportUserForm(forms.Form):
#     """
#     导入用户信息表单
#     """
#
#     error_messages = {
#         'file_extension': "只能上传 excel .xls 文件",
#     }
#     required_css_class = 'required'
#     excel_file = forms.Textarea
#
#     def clean_excel_file(self):
#         excel_file = self.cleaned_data.get('excel_file')
#         ext = get_extension(excel_file.name)
#
#         # 判断文件后缀
#         if ext not in ['xls']:
#             raise ValidationError(
#                 self.error_messages['file_extension'],
#                 code='file_extension',
#             )
#
#         return excel_file

