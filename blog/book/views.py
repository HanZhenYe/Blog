import json
import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator

from blog.settings import Redis
from .models import Book, BookContent
from note.views import page_limit
from tool.tokens import cookie_check, logging_check


# 书籍主页
@cookie_check
def index(request):
    if request.method == 'GET':
        page = request.GET.get('page')

        # 排除page不存在的情况
        if not page:
            page = 1

        # 排除page结构不正确的情况
        try:
            page = int(page)
        except Exception as e:
            dic = {
                'code': 22020,
                'error': '分页结构不正确'
            }
            return JsonResponse(dic)

        book_all = Book.objects.all()
        paginator = Paginator(book_all, 6)
        paginator_sum = paginator.num_pages

        # 排除page超出范围的情况
        if page <= 0 or page > paginator_sum:
            dic = {
                'code': 20117,
                'error': '对不起page值超出范围'
            }
            return JsonResponse(dic)

        book_data = paginator.page(page)

        # 判断是否有上一页
        if book_data.has_previous():
            front = True
            front_value = page - 1
        else:
            front = False
            front_value = page

        # 判断是否有下一页
        if book_data.has_next():
            after = True
            after_value = page + 1
        else:
            after = False
            after_value = 0

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

        # 整理书籍
        book_list = []
        for book in book_data:
            book_list.append({
                'id': book.id,
                'img': book.img
            })

        dic = {
            'book_list': book_list,
            'page': page,
            'front': front,
            'after': after,
            'front_value': front_value,
            'after_value': after_value,
            'page_count': page_limit(page, paginator.num_pages + 1),
            'user': user,
        }

        return render(request, 'book/book_index.html', dic)


# 书籍目录
@cookie_check
@logging_check('POST')
def book_catalog(request):
    if request.method == 'GET':
        book_id = request.GET.get('book_id')

        # 排除笔记ID不存在的情况
        if not book_id:
            dic = {
                'code': 21001,
                'error': '书籍ID不能为空'
            }
            return JsonResponse(dic)

        # 排除笔记ID不正确的情况
        try:
            book_id = int(book_id)
        except Exception as e:
            dic = {
                'code': 21002,
                'error': '书籍ID不为整数'
            }
            return JsonResponse(dic)

        try:
            book = Book.objects.get(id=book_id)
        except Exception as e:
            dic = {
                'code': 21003,
                'error': '书籍不存在'
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

        dic = {
            'id': book.id,
            'img': book.img,
            'title': book.title,
            'synopsis': book.synopsis,
            'author': book.author,
            'press': book.press,
            'pub_date': book.pub_date,
            'catalog': json.loads(book.catalog),
            'creation_time': book.creation_time,
            'user': user
        }
        return render(request, 'book/book_list.html', dic)

    if request.method == 'POST':
        book_id = request.POST.get('id')

        # 排除书籍ID不存在的情况
        if not book_id:
            dic = {
                'code': 21004,
                'error': '笔记ID不能为空'
            }
            return JsonResponse(dic)

        # 排除书籍ID格式不正确的情况
        try:
            book_id = int(book_id)
        except Exception as e:
            dic = {
                'code': 21005,
                'error': '笔记ID格式不正确'
            }
            return JsonResponse(dic)

        # 排除书籍不存在的情况
        try:
            book = Book.objects.get(id=book_id)
        except Exception as e:
            dic = {
                'code': 21006,
                'error': '笔记不存在'
            }
            return JsonResponse(dic)

        data = request.POST.get('data')

        # 创建目录内容
        data = json.loads(data)
        for yi in data:
            if yi['id'] == '-1':
                try:
                    yi['id'] = str(BookContent.objects.create(book=book, title=yi['name'], text='暂时没有内容').id)
                except Exception as e:
                    print('一级目录创建失败')
            if yi['cun']:
                for er in yi['er']:
                    if er['id'] == '-1':
                        try:
                            er['id'] = str(BookContent.objects.create(book=book, title=er['name'],text='暂时没有内容').id)
                        except Exception as e:
                            print('二级目录创建失败')
                    if er['cun']:
                        for san in er['san']:
                            if san['id'] == '-1':
                                try:
                                    san['id'] = str(BookContent.objects.create(book=book, title=san['name'], text='暂时没有内容').id)
                                except Exception as e:
                                    print('三级目录创建失败')

        # 获得当前时间格式: 2020.8.23
        date = datetime.datetime.now().strftime('%Y.%m.%d')
        # 拼接格式: 2020.8.23更新了《Django企业开发实战》
        book_data = '%s更新了《%s》' % (date, book.title)
        # 判断 book:date:list 键是否存在
        if Redis.exists('book:date:list'):
            # 获取　book:date:list　列表
            book_date_list = Redis.lrange('book:date:list', 0, -1)
            # 　排除　note_data　不在列表中的情况,　使得短期更新不重复
            if book_data.encode() not in book_date_list:
                Redis.lpush('book:date:list', book_data)
            # 列表裁剪
            if len(book_date_list) >= 20:
                Redis.ltrim('book:date:list', 0, 8)

        # 不存在时创建，并压入当前格式化的字符串
        else:
            Redis.lpush('book:date:list', book_data)

        book.catalog = json.dumps(data)
        book.save()

        return JsonResponse({'code': 200})


# 书籍详情页
@cookie_check
@logging_check('POST')
def book_details(request):

    # 获取书籍章节
    if request.method == 'GET':
        book_id = request.GET.get('id')

        # 排除书籍ID为空的情况
        if not book_id:
            dic = {
                'code': 22007,
                'error': '书籍ID不能为空'
            }
            return JsonResponse(dic)

        # 排除书籍ID格式不正确的情况
        try:
            book_id = int(book_id)
        except Exception as e:
            dic ={
                'code': 22008,
                'error': '书籍ID格式不正确'
            }
            return JsonResponse(dic)

        # 排除书籍不存在的情况
        try:
            book = Book.objects.get(id=book_id)
        except Exception as e:
            dic = {
                'code': 22009,
                'error': '书籍不存在'
            }
            return JsonResponse(dic)

        catalog_id = request.GET.get('catalog_id')

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

        # 返回书籍信息
        if not catalog_id:
            dic = {
                'switch': True,
                'book_id': book.id,
                'title': book.title,
                'img': book.img,
                'author': book.author,
                'synopsis': book.synopsis,
                'press': book.press,
                'pub_date': book.pub_date,
                'catalog': json.loads(book.catalog),
                'creation_time': book.creation_time,
                'user': user
            }

        # 返回目录信息
        else:

            # 排除书籍目录ID不正确的情况
            try:
                catalog_id = int(catalog_id)
            except Exception as e:
                dic = {
                    'code': 22010,
                    'error': '书籍目录ID不正确'
                }
                return JsonResponse(dic)

            # 排除书籍章节不存在的情况
            try:
                catalog = BookContent.objects.get(id=catalog_id)
            except Exception as e:
                dic = {
                    'code': 21011,
                    'error': '书籍章节不正确'
                }
                return JsonResponse(dic)

            dic = {
                'switch': False,
                'book_id': book.id,
                'title': book.title,
                'catalog_id': str(catalog.id),
                'chapter': catalog.title,
                'text': catalog.text,
                'catalog': json.loads(book.catalog),
                'user': user
            }

        return render(request, 'book/book.html', dic)

    # 书籍章节提交
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        catalog_id = request.POST.get('catalog_id')

        # 排除书籍ID不存在的情况
        if not book_id:
            dic = {
                'code': 22011,
                'error': '请输入书籍ID'
            }
            return JsonResponse(dic)

        # 排除书籍章节ID不存在的情况
        if not catalog_id:
            dic = {
                'code': 22012,
                'error': '请输入书籍章节ID'
            }
            return JsonResponse(dic)

        # 排除书籍ID和书籍章节ID不存在的情况
        try:
            book_id = int(book_id)
            catalog_id = int(catalog_id)
        except Exception as e:
            dic = {
                'code': 22013,
                'error': '书籍ID或书籍章节ID格式不正确'
            }
            return JsonResponse(dic)

        # 排除书籍不能存在的情况
        try:
            book = Book.objects.get(id=book_id)
        except Exception as e:
            dic = {
                'code': 22014,
                'error': '书籍不存在'
            }
            return JsonResponse(dic)

        # 排除书籍不存在该章节的情况
        try:
            content = book.bookcontent_set.get(id=catalog_id)
        except Exception as e:
            dic = {
                'code': 22015,
                'error': '书籍中没有该章节'
            }
            return JsonResponse(dic)

        text = request.POST.get('text')
        content.text = text
        content.save()

        return JsonResponse({'code': 200})

