# Generated by Django 2.2 on 2020-08-21 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='catalog',
            field=models.TextField(blank=True, verbose_name='笔记目录'),
        ),
        migrations.AlterField(
            model_name='note',
            name='img',
            field=models.ImageField(default='static/img/biji.jpg', upload_to='', verbose_name='封面'),
        ),
    ]
