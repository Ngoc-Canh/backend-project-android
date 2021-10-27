import calendar
import datetime
import json

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from app_config import LIST_VALID_IP
from app_common import Client, Timer
from core.models import Event, Holiday, DayOff
from core.service.jobs_scheduler import job_daily


class ValidateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self):
        result = job_daily()

        return Response({"msg": result}, 200)


class SaveDeviceToken(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token_device = request.data["token_device"]

        dict_token = {
            request.user.email: {
                "token_device": token_device
            }
        }

        with open('device_token.json', 'r') as openfile:
            listObj = json.load(openfile)

        for lst in listObj:
            if lst[f"{request.user.email}"]:
                lst[f"{request.user.email}"].update({"token_device": f"{token_device}"})
            else:
                listObj.append(dict_token)

        if not listObj:
            listObj.append(dict_token)

        with open("device_token.json", 'w') as json_file:
            json.dump(listObj, json_file,
                      indent=4,
                      separators=(',', ': '))


class GetEventView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            events = Event.objects.filter(created_by=request.user, is_active=True, created_date=Timer.get_today())
            now = Timer.get_time_now()
            metadata = {
                'valid_ip': validate_ip(request),
                'user': {"full_name": request.user.full_name},
                'event': None,
                'is_holiday': is_holiday(datetime.datetime.today().date()),
                "is_day_off": is_day_off(now.month, now.year)
            }

            for event in events:
                event_item = {
                    "created_at": event.created_at,
                    "event_type": event.event_type.event_name,
                }

                if metadata['event'] is None:
                    metadata['event'] = [event_item]
                else:
                    metadata['event'].append(event_item)

            return Response(metadata, status=200)
        except Exception as e:
            return Response({'event': {'status': "Error", 'msg': f"{str(e)}"}}, status=400)

    def post(self, request):
        try:
            token_device = request.data["token_device"]

            dict_token = {
                request.user.email: {
                    "token_device": token_device
                }
            }

            with open('device_token.json', 'r') as openfile:
                listObj = json.load(openfile)

            for lst in listObj:
                if lst[f"{request.user.email}"]:
                    lst[f"{request.user.email}"].update({"token_device": f"{token_device}"})
                else:
                    listObj.append(dict_token)

            if not listObj:
                listObj.append(dict_token)

            with open("device_token.json", 'w') as json_file:
                json.dump(listObj, json_file,
                          indent=4,
                          separators=(',', ': '))

            events = Event.objects.filter(created_by=request.user, is_active=True, created_date=Timer.get_today())
            now = Timer.get_time_now()
            metadata = {
                'valid_ip': validate_ip(request),
                'user': {"full_name": request.user.full_name},
                'event': None,
                'is_holiday': is_holiday(datetime.datetime.today().date()),
                "is_day_off": is_day_off(now.month, now.year)
            }

            for event in events:
                event_item = {
                    "created_at": event.created_at,
                    "event_type": event.event_type.event_name,
                }

                if metadata['event'] is None:
                    metadata['event'] = [event_item]
                else:
                    metadata['event'].append(event_item)

            return Response(metadata, status=200)
        except Exception as e:
            return Response({'event': {'status': "Error", 'msg': f"{str(e)}"}}, status=400)


class HistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            query_params = request.query_params
            month = query_params['month']
            year = query_params['year']
            events = Event.objects.filter(created_by=request.user, is_active=True,
                                          created_date__month=month, created_date__year=year)

            holiday = get_range_holidays(month=int(month), year=int(year))

            history_data = {
                'user': {"full_name": request.user.full_name},
                'event': None,
                'holiday': holiday,
                'day_off': get_day_off_with_month(month=int(month), year=int(year), user=request.user)
            }

            for event in events:
                event_item = {
                    "created_at": event.created_at,
                    "created_date": event.created_date,
                    "event_type": event.event_type.event_name,
                    "valid": True if event.user_ip in LIST_VALID_IP else False
                }

                if history_data['event'] is None:
                    history_data['event'] = [event_item]
                else:
                    history_data['event'].append(event_item)

            return Response(history_data, status=200)
        except Exception as e:
            return Response({'event': {'status': "Error", 'msg': f"{str(e)}"}}, status=400)


class APIHoliday(APIView):
    permission_class = (IsAuthenticated, )

    def get(self, request):
        if request.user.is_admin:
            data = Holiday.objects.all()
            return Response(data, status=200)
        else:
            return Response({'code': 500, 'status': 'NOK', 'msg': 'Bạn không có quyền truy cập'})

    def post(self, request):
        try:
            Holiday.create_holiday(**request.data)
            return Response({'code': 200, 'status': 'OK', 'msg': 'Thêm mới thành công'})
        except Exception as e:
            return Response({"code": 500, "msg": f"{str(e)}"})



def validate_ip(request):
    client_info = Client.get_client_info(request)
    user_ip = client_info['user_ip']
    VALIDATE_IPS = LIST_VALID_IP.split(', ')

    if user_ip in VALIDATE_IPS:
        return True
    else:
        return False


def is_holiday(date):
    for hld in Holiday.objects.filter():
        if hld.start_holiday <= date <= hld.end_holiday:
            return True
    return False


def get_day_off_with_month(month, year, user):
    last_day_in_month = get_number_day_in_month(month=month, year=year)

    ts_first_month = int(datetime.datetime(year, month, 1).timestamp())
    ts_last_month = int(datetime.datetime(year, month, last_day_in_month).timestamp())

    lst_result = []

    for df in DayOff.objects.filter(Q(start_date__month=month) & Q(start_date__year=year) |
                                    Q(end_date__month=month) & Q(end_date__year=year), is_active=True, created_by=user):
        if float(df.number_day_off).is_integer():
            for days in range(0, int(df.number_day_off - 1)):
                all_day = False
                morning = False
                afternoon = False
                next_day = df.start_date + datetime.timedelta(days=days)
                ts = int(datetime.datetime(next_day.year, next_day.month, next_day.day).timestamp())
                if ts_first_month <= ts <= ts_last_month:
                    all_day = True
                    lst_result.append({"date": next_day, "all_day": all_day,
                                       "morning": morning, "afternoon": afternoon, "type": df.type_off.name})
        else:
            for days in range(0, int(df.number_day_off + 0.5)):
                all_day = False
                morning = False
                afternoon = False
                next_day = df.start_date + datetime.timedelta(days=days)
                ts = int(datetime.datetime(next_day.year, next_day.month, next_day.day).timestamp())
                if ts_first_month <= ts <= ts_last_month:
                    if days == 0:
                        # Kiểm tra ngày đầu tiên có phải nửa ngày ko ?
                        hour_start_for_start_date = int(get_type_from_ts(fmt="%H", ts=df.ts_start_for_start_date))
                        hour_end_for_start_date = int(get_type_from_ts(fmt="%H", ts=df.ts_end_for_start_date))
                        if (hour_start_for_start_date + hour_end_for_start_date) == 24:
                            all_day = True

                        if hour_start_for_start_date > 12:
                            afternoon = True if not all_day else False
                        elif hour_start_for_start_date <= 12:
                            morning = True if not all_day else False

                        lst_result.append({"date": next_day, "all_day": all_day,
                                           "morning": morning, "afternoon": afternoon, "type": df.type_off.name})
                        continue

                    if days == int(df.number_day_off - 0.5):
                        hour_start_for_end_date = int(get_type_from_ts(fmt="%H", ts=df.ts_start_for_end_date))
                        hour_end_for_end_date = int(get_type_from_ts(fmt="%H", ts=df.ts_end_for_end_date))

                        if (hour_start_for_end_date + hour_end_for_end_date) == 24:
                            all_day = True

                        if hour_start_for_end_date > 12:
                            afternoon = True if not all_day else False
                        elif hour_start_for_end_date <= 12:
                            morning = True if not all_day else False

                        lst_result.append({"date": next_day, "all_day": all_day,
                                           "morning": morning, "afternoon": afternoon, "type": df.type_off.name})
                        continue

                    all_day = True
                    lst_result.append({"date": next_day, "all_day": all_day,
                                       "morning": morning, "afternoon": afternoon, "type": df.type_off.name})
    return lst_result


def is_day_off(month, year):
    hour_request = Timer.get_time_now().hour
    query = DayOff.objects.filter(Q(start_date__month=month) & Q(start_date__year=year) |
                                  Q(end_date__month=month) & Q(end_date__year=year), is_active=True)
    if not query:
        return False

    for dayoff in query:

        if dayoff.start_date <= datetime.datetime.today().date() <= dayoff.end_date:
            if float(dayoff.number_day_off).is_integer():
                # Nghỉ tròn ngày
                return True
            else:
                # Có nghỉ nửa ngày
                int_day_off = dayoff.number_day_off + 0.5
                for days in range(0, int(int_day_off)):
                    next_day = dayoff.start_date + datetime.timedelta(days=days)
                    if next_day == datetime.datetime.today().date():
                        if days == 0:
                            # Kiểm tra ngày đầu tiên có phải nửa ngày ko ?
                            hour_start_for_start_date = int(get_type_from_ts(fmt="%H", ts=dayoff.ts_start_for_start_date))
                            hour_end_for_start_date = int(get_type_from_ts(fmt="%H", ts=dayoff.ts_end_for_start_date))
                            if hour_start_for_start_date <= hour_request <= hour_end_for_start_date:
                                return True
                            else:
                                return False
                        if days == int(int_day_off):
                            # Kiểm tra ngày cuối cùng trong ngày nghỉ là 0.5 ngày ?
                            hour_start_for_end_date = int(get_type_from_ts(fmt="%H", ts=dayoff.ts_start_for_end_date))
                            hour_end_for_end_date = int(get_type_from_ts(fmt="%H", ts=dayoff.ts_end_for_end_date))
                            if hour_start_for_end_date <= hour_request <= hour_end_for_end_date:
                                return True
                            else:
                                return False
                        return True
                    return False


# def get_number_dayOff(ts1, ts2, ts3, ts4):
#     start = get_type_from_ts("%Y/%m/%d/%H", ts1).split("/")
#     end_of_start = get_type_from_ts("%Y/%m/%d/%H", ts2).split("/")
#     end = get_type_from_ts("%Y/%m/%d/%H", ts3).split("/")
#     end_of_end = get_type_from_ts("%Y/%m/%d/%H", ts4).split("/")
#
#     count = datetime.date(int(end[0]), int(end[1]), int(end[2])) - datetime.date(int(start[0]), int(start[1]),
#                                                                                  int(start[2]))
#     day = count.days + 1
#
#     if day == 1:
#         if (start[3] == "01" and end_of_start[3] == "12") and (end[3] == "13" and end_of_end[3] == "23"):
#             return day
#         if start[3] == "01" and end_of_start[3] == "12":
#             day = day - 0.5
#         if start[3] == "13" and end_of_start[3] == "23":
#             day = day - 0.5
#         return day
#     else:
#         if start[3] == "01" and end_of_start == "12":
#             day = day - 0.5
#         if start[3] == "12" and end_of_start == "23":
#             day = day - 0.5
#
#         if end[3] == "01" and end_of_end == "12":
#             day = day - 0.5
#         if end[3] == "12" and end_of_end == "23":
#             day = day - 0.5
#         return day


# def get_number_day_off(ts_start, ts_end, calculate=False):
#     start = get_type_from_ts("%Y/%m/%d/%H", ts_start).split("/")
#     end = get_type_from_ts("%Y/%m/%d/%H", ts_end).split("/")
#
#     count = datetime.date(int(end[0]), int(end[1]), int(end[2])) - datetime.date(int(start[0]), int(start[1]), int(start[2]))
#     day = count.days
#
#     if not calculate:
#         if day == 1 and start[3] == "1" and end[3] == "23":
#             return day
#
#         if start[3] == "12" or end[3] == "12":
#             day = day - 0.5
#
#         return day
#     else:
#         if float(day).is_integer():
#             return f"{ts_start}, {ts_start}, {ts_end}, {ts_end}"
#         else:
#             if start[3] == "12":
#                 strDate = f"{start[0]}/{start[1]}/{start[2]} {start[3]}"
#                 rs = datetime.datetime.strptime(strDate, "%Y/%m/%d %H")
#                 ts1 = datetime.datetime.timestamp(rs)
#             else:
#                 ts1 = ts_start
#
#             if end[3] == "12":
#                 strDate = f"{end[0]}/{end[1]}/{end[2]} {end[3]}"
#                 rs = datetime.datetime.strptime(strDate, "%Y/%m/%d %H")
#                 ts2 = datetime.datetime.timestamp(rs)
#             else:
#                 ts2 = ts_end
#
#             return f"{ts_start}, {ts1}, {ts_end}, {ts2}"


def get_range_holidays(month, year):
    last_day_in_month = get_number_day_in_month(month=month, year=year)

    ts_first_month = int(datetime.datetime(year, month, 1).timestamp())
    ts_last_month = int(datetime.datetime(year, month, last_day_in_month).timestamp())

    list_result = []

    for holiday in Holiday.objects.filter(Q(start_holiday__month=month) & Q(start_holiday__year=year) |
                                          Q(end_holiday__month=month) & Q(end_holiday__year=year)):
        if holiday.sum_day <= 1:
            list_result.append({"holiday": holiday.start_holiday,
                                "description": holiday.description})
        else:
            for i in range(0, holiday.sum_day):
                next_day = holiday.start_holiday + datetime.timedelta(days=i)
                ts_next_day = int(datetime.datetime(next_day.year, next_day.month, next_day.day).timestamp())
                if ts_first_month <= ts_next_day <= ts_last_month:
                    list_result.append({"holiday": next_day,
                                        "description": holiday.description})
    return list_result


def get_number_day_in_month(month, year):
    cal = calendar.Calendar()

    _calendar = list(cal.itermonthdays2(year, month))
    _, number_days_of_month = calendar.monthrange(year, month)
    return number_days_of_month


def get_type_from_ts(fmt, ts):
    if ts > 1000000000000:
        ts /= 1000
    return datetime.datetime.fromtimestamp(ts).strftime(fmt)


