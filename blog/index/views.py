import json
import datetime

from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.cache import cache_page

from blog.settings import Redis
from .models import RotationChart, Notice, User, LoginRecord
from article.models import Classification, Article
from article.views import time_disparity
from note.models import Note
from book.models import Book
from tool.tokens import token_encode, cookie_check


# 主页
@cookie_check
def index(request):
    if request.method == 'GET':
        rotation_chart = RotationChart.objects.all()
        notice = Notice.objects.filter(state=True)

        # 公告处理
        not_list = []
        for n in notice:
            not_list.append({'not_content': n.content})

        # 轮播图数量
        rot_max = len(rotation_chart)

        # 整理轮播图
        rotation_chart_list = []
        for ro in rotation_chart:
            rotation_chart_list.append({'img': ro.img})

        # 整理文章
        article = Article.objects.order_by('-creation_time')[0:5]
        article_list = []
        for art in article:
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

        # 获取全部分类
        cla_all = Classification.objects.all()
        cla_list = []
        for cla in cla_all:
            # 获取分类的文章数量
            number = cla.article_set.aggregate(count=Count('id'))
            cla_list.append({'name': cla.name, 'number': number['count']})

        # 整理笔记
        note = Note.objects.order_by('-update_time')[0:6]
        note_list = []
        for n in note:
            note_data = {
                'id': n.id,
                'img': n.img,
                'title': n.title
            }
            note_list.append(note_data)

        # 获取笔记更新信息
        note_date_list = []
        for note_date in Redis.lrange('note:date:list', 0, 7):
            note_date_list.append(note_date.decode())

        # 网站状态信息
        statue = {
            'ri_browse_ren': Redis.scard('ri:browse:ren'),
            'ri_browse_ci': Redis.get('ri:browse:ci').decode(),
            'sum_browse_ren': Redis.get('sum:browse:ren').decode()
        }

        # 获取书籍信息
        book_all = Book.objects.order_by('-update_time')[0:6]
        book_list = []
        for book in book_all:
            book_list.append({
                'id': book.id,
                'img': book.img
            })

        # 获取书籍更新信息
        book_date_list = []
        for book_date in Redis.lrange('book:date:list', 0, 7):
            book_date_list.append(book_date.decode())

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
            'rotation_chart': rotation_chart_list,
            'rot_max': range(rot_max),
            'article_list': article_list,
            'note_list': note_list,
            'cla_list': cla_list,
            'not_list': not_list,
            'statue': statue,
            'note_date_list': note_date_list,
            'user': user,
            'book_list': book_list,
            'book_date_list': book_date_list
        }
        return render(request, 'index/index.html', dic)


# 登录
@cookie_check
def login(request):
    # 获取登录页面
    if request.method == 'GET':

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
            'user': user
        }
        return render(request, 'index/login.html', dic)

    # 登录校验
    if request.method == 'POST':

        name = request.POST.get('name')
        password = request.POST.get('password')

        # 排除用户名为空的存在
        if not name:
            dic = {
                'code': 30110,
                'error': '请输入姓名'
            }
            return JsonResponse(dic)

        # 排除密码为空的情况
        if not password:
            dic = {
                'code': 30111,
                'error': '密码不能为空'
            }
            return JsonResponse(dic)

        user = User.objects.filter(name=name)
        if not user:
            dic = {
                'code': 30112,
                'error': '用户名或密码错误'
            }
            return JsonResponse(dic)

        if password not in user[0].password:
            dic = {
                'code': 30113,
                'error': '用户名或密码错误'
            }
            return JsonResponse(dic)

        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%m')
        LoginRecord.objects.create(name=name, record=date)

        token = token_encode(name, 60 * 60 * 24)

        dic = {
            'code': 200,
            'token': token.decode(),
        }
        response = HttpResponse(json.dumps(dic), content_type="application/json")
        response.set_cookie('user', token.decode(), 60 * 60 * 24)

        return response


# 退出
def quit(request):
    if request.method == 'POST':
        response = HttpResponse(json.dumps({'code': 200}), content_type="application/json")
        response.delete_cookie('user')
        return response


# 搜索
@cookie_check
def search(request):
    if request.method == 'GET':
        search_class = request.GET.get('class')

        # 排除非类型之外的情况
        if search_class not in ['article_class', 'article', 'note', 'book', 'tool']:
            dic = {
                'code': 30211,
                'error': '搜索类型不正确'
            }
            return JsonResponse(dic)

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

        # 文章分类
        if search_class == 'article_class':
            name = request.GET.get('name')

            # 排除分类名称不为空的情况
            if not name:
                dic = {
                    'code': 30212,
                    'error': '分类名称不能为空'
                }
                return JsonResponse(dic)

            try:
                classification = Classification.objects.get(name=name)
            except Exception as e:
                dic = {
                    'code': 30213,
                    'error': '文章分类不存在'
                }
                return JsonResponse(dic)

            article_data = classification.article_set.all()

            # 整理文章分类的文章
            article_list = []
            for art in article_data:
                disparity = time_disparity(art.creation_time)
                article_dic = {
                    'id': art.id,
                    'img': art.img,
                    'title': art.title,
                    'creation_time': art.creation_time,
                    'introduce': art.introduce,
                    'browse_number': art.browse_number,
                    'comment_number': art.comment_number,
                    'disparity': disparity
                }
                article_list.append(article_dic)

            # 获取所有文章分类
            cla_all = Classification.objects.all()
            cla_list = []
            for cla in cla_all:
                # 获取分类的文章数量
                number = cla.article_set.aggregate(count=Count('id'))
                cla_list.append({'name': cla.name, 'number': number['count']})

            dic = {
                'code': 200,
                'user': user,
                'data': {
                    'class': 'article_class',
                    'article_list': article_list,
                    'cla_list': cla_list,
                    'active': name,
                }
            }

        # 文章搜索
        elif search_class == 'article':
            name = request.GET.get('name')

            # 排除name不存在的情况
            if not name:
                article_data = Article.objects.all()
            else:
                article_data = Article.objects.filter(title__icontains=name)

            article_list = []
            for art in article_data:
                disparity = time_disparity(art.creation_time)
                article_dic = {
                    'id': art.id,
                    'img': art.img,
                    'title': art.title,
                    'creation_time': art.creation_time,
                    'introduce': art.introduce,
                    'browse_number': art.browse_number,
                    'comment_number': art.comment_number,
                    'disparity': disparity
                }
                article_list.append(article_dic)

            # 获取所有文章分类
            cla_all = Classification.objects.all()
            cla_list = []
            for cla in cla_all:
                # 获取分类的文章数量
                number = cla.article_set.aggregate(count=Count('id'))
                cla_list.append({'name': cla.name, 'number': number['count']})

            dic = {
                'code': 200,
                'user': user,
                'data': {
                    'class': 'article',
                    'article_list': article_list,
                    'cla_list': cla_list,
                     'active': name,
                     
                }
            }

        # 笔记搜索
        elif search_class == 'note':
            name = request.GET.get('name')

            if not name:
                note_data = Note.objects.all()
            else:
                note_data = Note.objects.filter(title__icontains=name)

            note_list = []
            for n in note_data:
                note_dic = {
                    'id': n.id,
                    'img': n.img,
                    'title': n.title
                }
                note_list.append(note_dic)
            dic = {
                'code': 200,
                'user': user,
                'data': {
                    'class': 'note',
                    'note_list': note_list,
                    'active': name
                }
            }

        # 书籍搜索
        elif search_class == 'book':
            name = request.GET.get('name')

            if not name:
                book_data = Book.objects.all()
            else:
                book_data = Book.objects.filter(title__icontains=name)

            book_list = []
            for book in book_data:
                book_list.append({
                    'id': book.id,
                    'img': book.img
                })

            dic = {
                'code': 200,
                'user': user,
                'data': {
                    'class': 'book',
                    'book_list': book_list,
                    'active': name
                }
            }

        elif search_class == 'tool':
            # 工具搜索
            pass

        return render(request, 'index/search.html', dic)


# 工具模块
def tool(request):
    return HttpResponse('<h1>待开发中</h1>')
