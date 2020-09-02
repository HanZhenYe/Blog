from django.contrib import admin
from .models import Notice, RotationChart, User, LoginRecord


# 轮播图
class RotationChartAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_display_links = ['id']


# 公告
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'state']
    list_display_links = ['id', 'content']
    list_editable = ['state']


# 用户
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'password', 'creation_time', 'Last_login_time']
    list_display_links = ['name']


# 用户登录记录
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'record']
    list_display_links = ['name']


admin.site.register(Notice, NoticeAdmin)
admin.site.register(RotationChart, RotationChartAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(LoginRecord, LoginRecordAdmin)
