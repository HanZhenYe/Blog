import json
import datetime

from django.db.models import F
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator

from blog.settings import Redis
from .models import Note, NoteContent
from tool.tokens import cookie_check, logging_check


# 笔记主页
@cookie_check
def note_index(request):
    if request.method == 'GET':
        page = request.GET.get('page')

        # 排除page为空的情况
        if not page:
            dic = {
                'code': 20115,
                'error': 'page值不能为空'
            }
            return JsonResponse(dic)

        # 排除page不为数字的情况
        try:
            page = int(page)
        except Exception as e:
            print('page不为整数')
            dic = {
                'code': 20116,
                'error': 'page不为整数'
            }
            return JsonResponse(dic)

        notes = Note.objects.all()
        paginator = Paginator(notes, 16)
        paginator_sum = paginator.num_pages

        # 排除page超出范围的情况
        if page <= 0 or page > paginator_sum:
            dic = {
                'code': 20117,
                'error': '对不起page值超出范围'
            }
            return JsonResponse(dic)

        note = paginator.page(page)

        # 判断是否有上一页
        if note.has_previous():
            front = True
            front_value = page - 1
        else:
            front = False
            front_value = page

        # 判断是否有下一页
        if note.has_next():
            after = True
            after_value = page + 1
        else:
            after = False
            after_value = 0

        # 整理笔记
        dic_list = []
        for n in note:
            note_dic = {
                'id': n.id,
                'title': n.title,
                'img': n.img
            }
            dic_list.append(note_dic)

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
            'data': dic_list,
            'page': page,
            'front': front,
            'after': after,
            'front_value': front_value,
            'after_value': after_value,
            'page_count': page_limit(page, paginator.num_pages + 1),
            'user': user
        }

        return render(request, 'note/note_index.html', dic)


# 笔记目录
@logging_check('POST')
@cookie_check
def note_catalog(request):
    if request.method == 'GET':

        note_id = request.GET.get('id')

        # 排除笔记ID不存在情况
        if not note_id:
            dic = {
                'code': 20110,
                'error': '请输入笔记ID'
            }
            return JsonResponse(dic)

        # 排除笔记ID不为整数的情况
        try:
            note_id = int(note_id)
        except Exception as e:
            print('笔记ID不为整数', e)
            dic = {
                'code': 20111,
                'error': '笔记ID必须为整数'
            }
            return JsonResponse(dic)

        # 获取笔记，并排除笔记不存在的情况
        try:
            note = Note.objects.get(id=note_id)
        except Exception as e:
            print('查询不到，笔记', e)
            dic = {
                'code': 20112,
                'error': '对不起，无法找到该笔记'
            }
            return JsonResponse(dic)

        if note.catalog:
            catalog = json.loads(note.catalog)
        else:
            catalog = ''

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
            'id': note.id,
            'title': note.title,
            'img': note.img,
            'creation_time': note.creation_time,
            'update_time': note.update_time,
            'browse_number': note.browse_number,
            'catalog': catalog,
            'user': user,
        }

        return render(request, 'note/note_list.html', dic)

    if request.method == 'POST':
        note_id = request.POST.get('id')
        data = request.POST.get('data')

        # 排除笔记ID不存在的情况s
        if not note_id:
            dic = {
                'code': 20113,
                'error': '笔记ID不存在'
            }
            return JsonResponse(dic)

        # 排除笔记ID不为整数的情况
        try:
            note_id = int(note_id)
        except Exception as e:
            print('笔记ID不为整数', e)
            dic = {
                'code': 20114,
                'error': '笔记ID不为整数'
            }
            return JsonResponse(dic)

        # 排除笔记不存在的情况
        try:
            note = Note.objects.get(id=note_id)
        except Exception as e:
            print('该笔记不存在', e)
            dic = {
                'code': 20115,
                'error': '该笔记不存在'
            }
            return JsonResponse(dic)

        # 将json转为python对象
        data_dic = json.loads(data)

        # 创建指定目录笔记内容
        for da in data_dic:
            for ex in da['ex']:
                if ex['id'] == '-1':
                    try:
                        note_content = NoteContent.objects.create(note=note, text='暂时没有内容')
                        ex['id'] = str(note_content.id)
                    except Exception as e:
                        print('目录笔记创建失败', e)

        # 将python对象转成json字符串，用于存储
        data = json.dumps(data_dic)
        note.catalog = data
        note.save()

        # 获得当前时间格式: 2020.8.23
        date = datetime.datetime.now().strftime('%Y.%m.%d')
        # 拼接格式: 2020.8.23更新了《前端笔记》
        note_data = '%s更新了《%s》' % (date, note.title)
        # 判断 note:date:list 键是否存在
        if Redis.exists('note:date:list'):
            # 获取　note:date:list　列表
            note_date_list = Redis.lrange('note:date:list', 0, -1)
            #　排除　note_data　不在列表中的情况,　使得短期更新不重复
            if note_data.encode() not in note_date_list:
                Redis.lpush('note:date:list', note_data)
            # 列表裁剪
            if len(note_date_list) >= 20:
                Redis.ltrim('note:date:list', 0, 8)

        # 不存在时创建，并压入当前格式化的字符串
        else:
            Redis.lpush('note:date:list', note_data)

        dic = {
            'code': 200,
            'data': '通过'
        }
        return JsonResponse(dic)


# 笔记内容页面
@cookie_check
@logging_check('POST')
def note_details(request):

    # 获取页面
    if request.method == 'GET':
        note_id = request.GET.get('note_id')
        content_id = request.GET.get('content_id')

        # 排除我笔记ID不存在的情况
        if not note_id:
            dic = {
                'code': 20117,
                'error': '请输入笔记ID'
            }
            return JsonResponse(dic)

        # 排除笔记ID不为整数的情况
        try:
            note_id = int(note_id)
        except Exception as e:
            print('笔记ID不为整数')
            dic = {
                'code': 20118,
                'error': '笔记ID或者笔记内容ID不为整数'
            }
            return JsonResponse(dic)

        # 排除笔记不存在的情况
        try:
            note = Note.objects.get(id=note_id)
        except Exception as e:
            print('笔记不存在', e)
            dic = {
                'code': 20119,
                'error': '笔记不存在'
            }
            return JsonResponse(dic)

        # 笔记内容ID不存在的情况
        if not content_id:
            try:
                Note.objects.filter(id=note_id).update(browse_number=F('browse_number') + 1)
            except Exception as e:
                print('笔记浏览累加失败')
                pass

            dic = {
                'id': note.id,
                'img': note.img,
                'title': note.title,
                'creation_time': note.creation_time,
                'update_time': note.update_time,
                'browse_number': note.browse_number,
                'catalog': json.loads(note.catalog),
                'index': False
            }
            return render(request, 'note/note_details.html', dic)

        # 排除笔记ID不为整数的情况
        try:
            content_id = int(content_id)
        except Exception as e:
            print('笔记内容ID不为整数')
            dic = {
                'code': 20118,
                'error': '笔记内容ID不为整数'
            }
            return JsonResponse(dic)

        # 排除笔记内容不存在的情况
        try:
            content_data = note.notecontent_set.get(id=content_id)
        except Exception as e:
            print('笔记内容不存在', e)
            dic = {
                'code': 20119,
                'error': '笔记内容不存在'
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
            'id': note.id,
            'title': note.title,
            'text': content_data.text,
            'content_id': str(content_data.id),
            'catalog': json.loads(note.catalog),
            'index': True,
            'user': user
        }

        return render(request, 'note/note_details.html', dic)

    # 笔记内容提交
    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        content_id = request.POST.get('content_id')
        text = request.POST.get('text')

        # 排除笔记ID不存在的情况
        if not note_id:
            dic = {
                'code': 20121,
                'error': '笔记ID不存在'
            }
            return JsonResponse(dic)

        # 排除笔记内容ID不存在的情况
        if not content_id:
            dic = {
                'code': 20122,
                'error': '笔记内容ID不存在的情况'
            }
            return JsonResponse(dic)

        try:
            note_id = int(note_id)
            content_id = int(content_id)
        except Exception as e:
            print('笔记ID不存在或笔记内容不存在')
            dic = {
                'code': 20123,
                'error': '笔记ID不存在或笔记内容不存在'
            }
            return JsonResponse(dic)

        # 排除笔记不存在或笔记内容不存在的情况
        try:
            note = Note.objects.get(id=note_id)
            content = note.notecontent_set.get(id=content_id)
        except Exception as e:
            print('笔记不存在或笔记内容不存在')
            dic = {
                'code': 20123,
                'error': '笔记不存在或笔记内容不存在'
            }
            return JsonResponse(dic)

        # 获得当前时间格式: 2020.8.23
        date = datetime.datetime.now().strftime('%Y.%m.%d')
        # 拼接格式: 2020.8.23更新了《前端笔记》
        note_data = '%s更新了《%s》' % (date, note.title)
        # 判断 note:date:list 键是否存在
        if Redis.exists('note:date:list'):
            # 获取　note:date:list　列表
            note_date_list = Redis.lrange('note:date:list', 0, -1)
            # 　排除　note_data　不在列表中的情况,　使得短期更新不重复
            if note_data.encode() not in note_date_list:
                Redis.lpush('note:date:list', note_data)
            # 列表裁剪
            if len(note_date_list) >= 20:
                Redis.ltrim('note:date:list', 0, 8)

        # 不存在时创建，并压入当前格式化的字符串
        else:
            Redis.lpush('note:date:list', note_data)

        content.text = text
        content.save()

        return JsonResponse({'code': 200})


# 分页限制
def page_limit(page, page_count):
    '''
    :param page: 当前分页
    :param request: 分页总数
    :return: 返回切割后的分页列表
    '''

    page_list = [i for i in range(page_count)]
    q = h = page
    i = False
    j = False

    while True:
        if (q - 1) == 0:
            i = True
        else:
            q -= 1

        if h == page_count:
            j = True
        else:
            h += 1

        # 分页列表的最大长度
        if len(page_list[q:h]) == 8:
            break

        if i and j:
            break
    return page_list[q: h]
