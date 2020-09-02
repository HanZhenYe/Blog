# Generated by Django 2.2 on 2020-08-26 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0005_notice_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='用户名')),
                ('record', models.CharField(max_length=50, verbose_name='登录记录')),
            ],
            options={
                'verbose_name': '登录记录',
                'verbose_name_plural': '登录记录',
                'db_table': 'login_record',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='用户名')),
                ('password', models.CharField(max_length=20, verbose_name='密码')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('Last_login_time', models.CharField(max_length=20, verbose_name='上次登录')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'user',
            },
        ),
    ]
