from django.contrib import admin

from .models import Book, BookContent


# 书籍后台显示
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'press', 'creation_time', 'update_time']
    list_display_links = ['title']
    search_fields = ['title']


# 书籍内容后台显示
class BookContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'book']
    list_display_links = ['title']


admin.site.register(Book, BookAdmin)
admin.site.register(BookContent, BookContentAdmin)
