from django import forms
# 引入验证码的CaptchaField
from captcha.fields import CaptchaField


# 表单
class RegisterFrom(forms.Form):
    # 邮箱
    email = forms.EmailField(required=True, error_messages={'invalid': '请填写正确的邮箱地址'})
    # 密码
    password = forms.CharField(required=True, min_length=6, error_messages={'min_length': '密码不能少于6位'})
    rePassword = forms.CharField(required=True, min_length=6, error_messages={'min_length': '密码不能少于6位'})
    # # 验证码
    # captcha = CaptchaField(required=True, error_messages={'invalid': '验证码错误'})
