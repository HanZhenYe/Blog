# Generated by Django 2.2 on 2020-08-29 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='synopsis',
            field=models.CharField(default='暂时没有简介', max_length=100, verbose_name='简介'),
        ),
    ]
