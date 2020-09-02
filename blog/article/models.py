from django.db import models


# 分类
class Classification(models.Model):
    name = models.CharField('分类名称', max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'classification'
        verbose_name = '分类'
        verbose_name_plural = verbose_name


# 文章
class Article(models.Model):
    title = models.CharField('标题', max_length=40)
    img = models.ImageField('封面', blank=True, upload_to='static/img')
    creation_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    introduce = models.CharField('简介', max_length=70, blank=True)
    content = models.TextField('文章内容', blank=True)
    browse_number = models.IntegerField('浏览量', default=0)
    comment_number = models.IntegerField('评论量', default=0)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'article'
        verbose_name = '文章'
        verbose_name_plural = verbose_name
