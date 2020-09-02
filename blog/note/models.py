from django.db import models


# 笔记目录
class Note(models.Model):
    title = models.CharField('笔记名称', max_length=40)
    catalog = models.TextField('笔记目录', blank=True, default='[{"mu": "\u6682\u65f6\u6ca1\u6709\u5185\u5bb9", "ex": []}]')
    img = models.ImageField('封面', upload_to='static/img', default='static/img/biji.jpg')
    creation_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    browse_number = models.IntegerField('浏览量', default=0)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'note'
        verbose_name = '笔记目录'
        verbose_name_plural = verbose_name


# 笔记内容
class NoteContent(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    text = models.TextField('内容')

    class Meta:
        db_table = 'note_content'
        verbose_name = '内容'
        verbose_name_plural = verbose_name
