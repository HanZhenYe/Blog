# Generated by Django 2.2 on 2020-08-20 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0004_article_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='img',
            field=models.ImageField(blank=True, upload_to='img', verbose_name='封面'),
        ),
    ]
