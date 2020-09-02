import time

import jwt
from django.http import JsonResponse

from index.models import User

TOKEN_KEY = 'we@#$%^88PPmd^&'


def logging_check(*method):
    def _logging_check(func):
        def warapps(request, *args, **kwargs):
            # method中没有值
            if not method:
                return func(request, *args, **kwargs)
            else:
                # 判断是否需要校验
                if request.method not in method:
                    return func(request, *args, **kwargs)
                else:
                    # 该处要进行token的校验
                    # 从请求头中取出token
                    token = request.POST.get('token')
                    # 没有token
                    if not token:
                        dic = {
                            'code': 40110,
                            'error': '请先登录'
                        }
                        return JsonResponse(dic)
                    else:
                        # 捕获token校验失败异常
                        try:
                            res = jwt.decode(token, TOKEN_KEY, algorithms='HS256')
                        except Exception as e:
                            dic = {
                                'code': 40110,
                                'error': '请先登录'
                            }
                            return JsonResponse(dic)
                        try:
                            user = User.objects.get(name=res['username'])
                        except Exception as e:
                            dic = {
                                'code': 40110,
                                'error': '请先登录'
                            }
                            return JsonResponse(dic)

            return func(request, *args, **kwargs)
        return warapps
    return _logging_check


# 生成koken
def token_encode(username, times):
    token = jwt.encode({'exp':time.time()+times, 'username': username}, TOKEN_KEY, 'HS256')
    return token


# 解token
def token_decode(token):
    return jwt.decode(token, TOKEN_KEY, 'HS256')


# 解cookie
def cookie_check(func):
    def warapps(request, *args, **kwargs):
        user_token = request.COOKIES.get('user')
        if not user_token:
            request.userIF = False
            return func(request, *args, **kwargs)

        try:
            user_jie = token_decode(user_token)
        except Exception as e:
            request.userIF = False
            return func(request, *args, **kwargs)

        try:
            user = User.objects.get(name=user_jie['username'])
        except Exception as e:
            request.userIF = False
            return func(request, *args, **kwargs)

        request.userIF = True
        request.name = user_jie['username']
        return func(request, *args, **kwargs)
    return warapps
