from .models import *
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect



# Create your views here.
def home(request):
    return render(request, 'index.html')


def loginView(request):
    user_email = request.POST.get('user_email', '')  # 后面的''表示获取不到user就赋值空
    pass_word = request.POST.get('pwd', '')
    # if user_name=='admin' and pass_word=='1':
    if user_email and pass_word:
        exit_user = UserInfo.objects.filter(email=user_email, password=pass_word).count()
        if exit_user >= 1:
            request.session['user_email'] = user_email
            request.session['is_login'] = True
            request.session.set_expiry(24*60*60)
            return render(request, 'index.html')
        else:
            exit_user_2 = UserInfo.objects.filter(email=user_email)
            if exit_user_2:
                # return HttpResponse("帐号密码错误！")
                messages.error(request, '帐号密码错误！')
                return render(request, 'login.html')
            else:
                # return HttpResponse("帐号不存在，请注册！")
                messages.error(request, '帐号不存在，请注册！')
                return render(request, 'login.html')
    else:
        # return HttpResponse("请输入正确用户名和密码！")
        messages.error(request, '请输入正确用户名和密码！')
        return render(request, 'login.html')


# 用户退出
def user_logout(request):
    del request.session['user_email']
    del request.session['is_login']
    # request.session['is_login'] = False
    return redirect('home')


from .forms import RegisterFrom
from .models import UserInfo
# make_password引入密码加密的函数
from django.contrib.auth.hashers import make_password
# Create your views here.
from .email_util import send_email


def register(request):
    # 验证form提交的数据
    form = RegisterFrom(request.POST)
    # 判断是否合法
    if form.is_valid():
        # 判断密码是否一致
        email = form.cleaned_data['email']
        pwd = form.cleaned_data['password']
        rePwd = form.cleaned_data['rePassword']
        # 两次密码不一致
        if pwd != rePwd:
            # 返回注册页面和错误信息
            # return HttpResponse('两次密码不一致!')
            messages.error(request, '两次密码不一致!')
            return render(request, 'register.html')
        # 判断用户是否存在
        # 根据email查找用户, 如果用户存在, 返回错误信息
        if UserInfo.objects.filter(email=email):
            # 用户已存在
            # return HttpResponse('该用户已存在!')
            messages.error(request, '该用户已存在!')
            return render(request, 'register.html')
        # 创建用户
        user = UserInfo.objects.create(email=email, password=pwd)
        # 对用户传递过来的密码进行加密, 将加密之后的数据进行保存
        # 账户状态 未激活
        user.is_active = 0
        # 保存为邮箱地址, 可以使用邮箱登录后台
        user.username = email
        # 保存用户
        user.save()
        # 发送注册邮件
        messages.success(request, '注册成功！请登录')
        return render(request, 'login.html')
        # if send_email(email, send_type='app'):
        #     # 注册邮件发送成功
        #     messages.success(request, '注册成功！')
        #     return HttpResponseRedirect(reverse('login'))
        #     # return HttpResponse('恭喜您注册成功, 激活邮件已发送至您的邮箱, 请登录后进行激活操作')
        # else:
        #     # return HttpResponse('恭喜您注册成功, 激活邮件发送')
        #     messages.success(request, '注册成功！')
        #     return HttpResponseRedirect(reverse('login'))
    else:
        # 返回form表单
        # 返回注册页面, 信息回填, 显示错误信息
        return render(request, 'register.html')
