import datetime

from ua_parser import user_agent_parser

import core.models
from app_config import STATUS_WAITING


class Timer(object):
    @classmethod
    def get_today(cls):
        today = datetime.datetime.today()
        return today.strftime("%Y-%m-%d")

    @classmethod
    def get_time_now(cls):
        return datetime.datetime.now()

    @classmethod
    def get_timestamp_now(cls):
        ts = datetime.datetime.now().timestamp()
        return ts

    @classmethod
    def is_on_leave(cls, user, event_time):
        dayOff = core.models.DayOff.objects.filter(created_by=user, manager_confirm__code=STATUS_WAITING)

        for days in dayOff:
            if days.start_date <= event_time <= days.end_date:
                return False
        return True


class Client(object):
    @classmethod
    def get_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ':' in ip:
            ip = ip.split(':')[0]
        return ip

    @classmethod
    def get_platform(cls, request):
        user_agent = request.META['HTTP_USER_AGENT']
        parser = user_agent_parser.ParseOS(user_agent)
        platform = parser.get('family', None)
        return platform

    @classmethod
    def get_client_info(cls, request):
        return {
            'user_ip': cls.get_ip(request)
        }
