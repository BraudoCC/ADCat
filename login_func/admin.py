from django.contrib import admin

# Register your models here.

from .models import UserInfo, EmailVeriRecord


# Register your models here.


# 注册自定义的用户模型
class UserInfoAdmin(admin.ModelAdmin):
    # 展示的字段
    list_display = ['email']
    # 根据某些字段进行搜索, 一般不会填写带有时间和日期的字段
    # search_fields = ['username', 'nick_name', 'email', 'mobile']
    # # 筛选器
    # list_filter = ['birday']


# 注册数据模型和后台管理里
admin.site.register(UserInfo, UserInfoAdmin)


class EmailAdmin(admin.ModelAdmin):
    list_display = ['code', 'email', 'send_time', 'email_type']
    search_fields = ['code', 'email']
    list_filter = ['send_time', 'exprie_time']


admin.site.register(EmailVeriRecord, EmailAdmin)
