from django.contrib import admin

from .models import Note, NoteContent


# 后台显示笔记
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'creation_time', 'update_time', 'browse_number']
    list_display_links = ['title']
    search_fields = ['id', 'title']


# 后台显示笔记内容
class NoteContentAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_display_links = ['id']
    search_fields = ['id']


admin.site.register(Note, NoteAdmin)
admin.site.register(NoteContent, NoteContentAdmin)
