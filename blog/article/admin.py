from django.contrib import admin
from .models import Article, Classification


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'update_time', 'creation_time', 'browse_number', 'comment_number']
    list_display_links = ['title']
    search_fields = ['id', 'title']


class ClassificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']
    search_fields = ['name']


admin.site.register(Article, ArticleAdmin)
admin.site.register(Classification, ClassificationAdmin)


admin.site.site_header = '用户登录'
admin.site.site_title = '欢迎'
