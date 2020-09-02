from django.db import models


# 轮播图
class RotationChart(models.Model):
    img = models.ImageField('图片', upload_to='static/img')

    class Meta:
        db_table = 'rotation_chart'
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name


# 公告
class Notice(models.Model):
    content = models.CharField('内容', max_length=40)
    state = models.BooleanField('状态')

    class Meta:
        db_table = 'notice'
        verbose_name = '公告'
        verbose_name_plural = verbose_name


# 用户
class User(models.Model):
    name = models.CharField('用户名', max_length=20)
    password = models.CharField('密码', max_length=20)
    token = models.CharField('token', max_length=200, blank=True)
    creation_time = models.DateTimeField('创建时间', auto_now_add=True)
    Last_login_time = models.CharField('上次登录', max_length=20, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


# 登录记录
class LoginRecord(models.Model):
    name = models.CharField('用户名', max_length=40)
    record = models.CharField('登录记录', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'login_record'
        verbose_name = '登录记录'
        verbose_name_plural = verbose_name

