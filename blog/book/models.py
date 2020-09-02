from django.db import models


# 书籍
class Book(models.Model):
    title = models.CharField('书名', max_length=50)
    img = models.ImageField('封面', upload_to='static/img', blank=True)
    author = models.CharField('作者', max_length=30)
    synopsis = models.CharField('简介', max_length=100, default='暂时没有简介')
    press = models.CharField('出版社', max_length=20)
    pub_date = models.DateField('出版时间')
    catalog = models.TextField('目录', blank=True)
    creation_time = models.DateField('入手时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'
        verbose_name = '书籍'
        verbose_name_plural = verbose_name


# 书籍内容
class BookContent(models.Model):
    title = models.CharField('章节', max_length=30, blank=True)
    text = models.TextField('内容')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        db_table = 'book_content'
        verbose_name = '书籍内容'
        verbose_name_plural = verbose_name
