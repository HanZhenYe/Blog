import datetime

from blog.settings import Redis
from django.utils.deprecation import MiddlewareMixin


class MyMW(MiddlewareMixin):

    def process_request(self, request):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        # 当两个时间不相同时
        if Redis.get('date').decode() not in date:
            # 更新最新时间
            Redis.set('date', date)
            # 日浏览人数归零
            Redis.delete('ri:browse:ren')
            Redis.sadd('ri:browse:ren', request.META['REMOTE_ADDR'])
            # 日浏览次数归零
            Redis.set('ri:browse:ci', 1)
            # 总浏览次数加1
            Redis.incr('sum:browse:ren')
        else:
            # 浏览人数添加
            Redis.sadd('ri:browse:ren', request.META['REMOTE_ADDR'])
            # 浏览次数增加
            if Redis.sadd('ri:ip', request.META['REMOTE_ADDR']):
                # 两秒后过期
                Redis.expire('ri:ip', 2)
                # 日浏览加1
                Redis.incr('ri:browse:ci')
                # 总浏览加1
                Redis.incr('sum:browse:ren')
        return None
