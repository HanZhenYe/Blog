import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F, Count
from django.core.paginator import Paginator

from note.views import page_limit
from .models import Article, Classification
from tool.tokens import cookie_check, logging_check


# 获取文章内容
@cookie_check
@logging_check('POST')
def articles(request):
    if request.method == 'GET':
        article_id = request.GET.get('id')

        if not article_id:
            dic = {
                'code': 10112,
                'error': '文章不存在'
            }
            return JsonResponse(dic)

        # 排除文章ID不为数字的情况
        try:
            article_id = int(article_id)
        except Exception as e:
            print('文章ID不为数字')
            dic = {
                'code': 10110,
                'error': '该文章不存在'
            }
            return JsonResponse(dic)

        # 捕获浏览累加异常
        try:
            Article.objects.filter(id=article_id).update(browse_number=F('browse_number') + 1)
        except Exception as e:
            print('浏览量累加失败', e)

        # 排除文章不存在的情况
        try:
            article = Article.objects.get(id=article_id)
        except Exception as e:
            print('文章ID不存在', e)
            dic = {
                'code': 10111,
                'error': '该文章不存在'
            }
            return JsonResponse(dic)

        # 取出下一篇文章
        article_upper_data = Article.objects.filter(id__gt=article_id).first()

        # 取出上一篇文章
        article_lower_data = Article.objects.filter(id__lt=article_id).last()

        # 判断是否有下一篇文章
        if article_upper_data:
            article_upper = {
                'id': article_upper_data.id,
                'title': article_upper_data.title
            }
        else:
            article_upper = False

        # 判断是否有上一篇文章
        if article_lower_data:
            article_lower = {
                'id': article_lower_data.id,
                'title': article_lower_data.title
            }
        else:
            article_lower = False

        # 获取分类
        classification = article.classification.name

        disparity = time_disparity(article.creation_time)

        # 用户
        if request.userIF:
            user = {
                'userIF': True,
                'name': request.name
            }
        else:
            user = {
                'userIF': False,
            }

        # 数据整理
        dic = {
            'id': article.id,
            'title': article.title,
            'creation_time': article.creation_time,
            'browse_number': article.browse_number,
            'comment_number': article.comment_number,
            'html': article.content,
            'disparity': disparity,
            'article_upper': article_upper,
            'article_lower': article_lower,
            'classification': classification,
            'user': user
        }

        return render(request, 'article/article.html', dic)

    if request.method == 'POST':
        data = request.POST.get('data')
        id = request.POST.get('id')
        introduce = request.POST.get('introduce')

        # 排除文章ID不为数字的情况
        try:
            id = int(id)
        except Exception as e:
            print('文章ID不是数字')
            dic = {
                'code': 10110,
                'eroor': '该文章不存在'
            }
            return JsonResponse(dic)

        # 排除文章不存在的情况
        try:
            article = Article.objects.get(id=id)
        except Exception as e:
            print('该文章不存在')
            dic = {
                'code': 10111,
                'error': '该文章不存在'
            }
            return JsonResponse(dic)

        article.content = data
        article.introduce = introduce
        article.save()

        dic = {
            'code': 200,
            'data': '修改成功'
        }

        return JsonResponse(dic)


# 文章主页,获取文章列表
@cookie_check
def article_index(request):
    if request.method == 'GET':

        # 按照时间降序排序
        article_all = Article.objects.order_by('-creation_time')

        # 使用分页
        paginator = Paginator(article_all, 10)
        page = paginator.page(1)

        article_list = []
        for art in page.object_list:
            disparity = time_disparity(art.creation_time)
            article_dic = {
                'id': art.id,
                'img': art.img,
                'title': art.title,
                'introduce': art.introduce,
                'creation_time': art.creation_time.strftime('%Y年%m月%d日 %H:%m'),
                'browse_number': art.browse_number,
                'comment_number': art.comment_number,
                'disparity': disparity
            }
            article_list.append(article_dic)

        classif = Classification.objects.all()

        # 分类列表
        classif_list = []
        for cl in classif:
            # 获取分类的文章数量
            number = cl.article_set.aggregate(count=Count('id'))
            classif_list.append({'name': cl.name, 'number': number['count']})

        # 用户
        if request.userIF:
            user = {
                'userIF': True,
                'name': request.name
            }
        else:
            user = {
                'userIF': False,
            }

        dic = {
            'user': user,
            'article_list': article_list,
            'classif_list': classif_list,
            'page_count': range(1, paginator.num_pages + 1)[:7]
        }

        return render(request, 'article/article_index.html', dic)


# 获取指定页数的数据
def article_page(request):
    if request.method == 'GET':
        page = request.GET.get('page')
        article_class = request.GET.get('article_class')

        # 判空处理
        if not page:
            dic = {
                'code': 10113,
                'error': '对不起，资源不存在'
            }
            return JsonResponse(dic)

        # 判空处理
        if not article_class:
            dic = {
                'code': 10114,
                'error': '对不起，资源不存在'
            }
            return JsonResponse(dic)

        # 排除指定类型之外的情况
        if article_class not in ['new', 'most']:
            dic = {
                'code': 10115,
                'error': '对不起，资源不存在'
            }
            return JsonResponse(dic)

        # 排除分页不为整数的情况
        try:
            page = int(page)
        except Exception as e:
            dic = {
                'code': 10115,
                'error': '对不起，资源不存在'
            }
            return JsonResponse(dic)

        if article_class in 'new':
            paclass = 1
            article_all = Article.objects.order_by('-creation_time')
        else:
            paclass = 2
            article_all = Article.objects.order_by('-browse_number')

        paginator = Paginator(article_all, 10)

        # 排除分页超出范围的情况
        if page < 1 or page > paginator.num_pages:
            dic = {
                'code': 10115,
                'error': '对不起，资源不存在'
            }
            return JsonResponse(dic)

        page_data = paginator.page(page)

        article_list = []
        for art in page_data.object_list:
            disparity = time_disparity(art.creation_time)
            article_dic = {
                'id': art.id,
                'img': str(art.img),
                'title': art.title,
                'introduce': art.introduce,
                'creation_time': art.creation_time.strftime('%Y年%m月%d日 %H:%m'),
                'browse_number': art.browse_number,
                'comment_number': art.comment_number,
                'disparity': disparity
            }
            article_list.append(article_dic)

        dic = {
            'code': 200,
            'data': {
                'article_list': article_list,
                'page': page,
                'paclass': paclass,
                'page_count': page_limit(page, paginator.num_pages + 1)
            }
        }
        return JsonResponse(dic)


# 获取时间差
def time_disparity(creation_time):
    # 获取当前时间
    current = datetime.datetime.now()
    # admin时间格式化，返回字符串
    before_date_str = creation_time.strftime('%Y-%m-%d %H:%m')
    # 字符串类型转datetime类型
    before_date = datetime.datetime.strptime(before_date_str, '%Y-%m-%d %H:%M')
    # 算时间差,并返回
    return current.__sub__(before_date).days
