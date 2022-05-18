from django.contrib.auth import PermissionDenied

from v1.validators import CaptchaValidation


def _get_permission_codename(prem, model):
    """
    Return the codename of the permission for the specified permission.
    """
    return '%s_%s' % (prem, model.model_name)


def _check_permission(request, name, model_meta):
    codename = _get_permission_codename(name, model_meta)

    if not request.user.has_perm('%s.%s' % (model_meta.app_label, codename)):
        raise PermissionDenied()


def validate(validator):
    """
    数据验证视图装饰器, 验证成功后调用视图，验证失败后直接返回错误信息

    :param validator: 验证器列表
    """

    def out_decorator(func):
        def decorator(cls, request):
            if isinstance(validator, tuple) or isinstance(validator, list):

                validations = []

                for item in validator:
                    validation = item(data=getattr(request, func.__name__.upper()))

                    if not isinstance(validation, CaptchaValidation):
                        validations.append(validation)

                    if not validation.is_valid():

                        data = {'errors': validation.errors, 'form_errors': True}

                        # 验证码错误
                        if isinstance(validation, CaptchaValidation):
                            data['captcha_errors'] = True

                        return cls.failed('请求失败!', data=data)

                return func(cls, request, validations) if len(validations) > 1 else func(cls, request, validations[0])

            validation = validator(data=getattr(request, func.__name__.upper()))

            if validation.is_valid():
                return func(cls, request, validation)

            return cls.failed('请求失败!', data={'errors': validation.errors, 'form_errors': True})

        return decorator

    return out_decorator


def permissions(*args):
    """
    权限校验视图装饰器

    使用方法: @permissions((Model, prem), ...)
    可以校验多个权限

    # [prem]: delete view change add
    @permissions((django.contrib.auth.models.AbstractUser, '[prem]'), ....)
    @permissions((django.contrib.auth.models.AbstractUser, ('[prem]', ....)), ....)
    def post(self, request):
        ...
    """

    def out_decorator(func):
        def decorator(cls, request):

            for item in args:
                if len(item) < 2:
                    raise ValueError()

                model_meta = item[0]._meta

                # 如果不是字符串, 说明需要一个 Model 校验多个权限
                if not isinstance(item[1], str):
                    # 循环校验权限
                    for n in item[1]:
                        _check_permission(request, n, model_meta)
                else:
                    # 校验权限
                    _check_permission(request, item[1], model_meta)

            return func(cls, request)
        return decorator
    return out_decorator
