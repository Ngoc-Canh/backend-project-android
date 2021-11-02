import datetime

from dateutil import parser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import DayOff


class ListDayOff(APIView):
    permission_class = (IsAuthenticated, )

    def get(self, request):
        dayoffs = DayOff.objects.filter(is_active=True, created_by=request.user).order_by("manager_confirm",
                                                                                          "-last_update")
        result = {
            'data': []
        }
        for dayOff in dayoffs:
            item = {
                "id": dayOff.id,
                "start_date": dayOff.start_date,
                "end_date": dayOff.end_date,
                "type": ", ".join(i.name for i in dayOff.type_off.all()),
                "created_date": datetime.datetime.fromtimestamp(dayOff.last_update).date(),
                "manager_confirm": dayOff.manager_confirm.code,
                "total_dayOff": dayOff.number_day_off
            }
            result['data'].append(item)
        return Response(data=result, status=200)

    def post(self, request):
        try:
            data = request.data
            number_day = get_number_dayOff(data['ts_start_for_start_date'], data['ts_end_for_start_date'],
                                           data['ts_start_for_end_date'], data['ts_end_for_end_date'])
            start_date = parser.parse(data['start_date'])
            end_date = parser.parse(data['end_date'])

            if number_day > request.user.total_dayOff:
                return Response({'msg': "Số ngày phép của bạn còn lại không đủ."}, status=404)

            if start_date > end_date:
                return Response({'msg': "Ngày kết thúc không thể lớn hơn ngày bắt đầu."}, status=404)

            result = {
                "number_day_off": number_day,
                "ts_start_for_start_date": data['ts_start_for_start_date'],
                "ts_end_for_start_date": data['ts_end_for_start_date'],
                "ts_start_for_end_date": data['ts_start_for_end_date'],
                "ts_end_for_end_date": data['ts_end_for_end_date'],
                "type_off": request.data['type'],
                "start_date": start_date,
                "end_date": end_date,
                "created_by": request.user,
            }

            query = DayOff.objects.filter(start_date__range=[result["start_date"], result["end_date"]],
                                          created_by=result['created_by'], is_active=True)
            if not query:
                DayOff.create_day_off(**result)
                return Response({'msg': 'Tạo mới thành công'}, status=202)
            else:
                return Response({'msg': 'Ngày nghỉ đã được tạo. Vui lòng kiểm tra lại'}, status=404)
        except Exception as e:
            return Response({'msg': f'{str(e)}'}, status=500)

    def delete(self, request, pk):
        try:
            dayoffs = DayOff.objects.get(id=pk, created_by=request.user)
            if dayoffs:
                return Response({"msg": "Không tồn tại bản ghi."}, status=400)

            dayoffs.is_active = False
            dayoffs.save()
            return Response({"msg: Hủy bỏ yêu cầu thành công"}, status=200)
        except Exception as e:
            return Response({f"msg: {str(e)}"}, status=400)


def get_number_dayOff(ts1, ts2, ts3, ts4):
    start = get_type_from_ts("%Y/%m/%d/%H", ts1).split("/")
    end_of_start = get_type_from_ts("%Y/%m/%d/%H", ts2).split("/")
    end = get_type_from_ts("%Y/%m/%d/%H", ts3).split("/")
    end_of_end = get_type_from_ts("%Y/%m/%d/%H", ts4).split("/")

    count = datetime.date(int(end[0]), int(end[1]), int(end[2])) - datetime.date(int(start[0]), int(start[1]),
                                                                                 int(start[2]))
    day = count.days + 1

    if day == 1:
        if (start[3] == "01" and end_of_start[3] == "12") and (end[3] == "13" and end_of_end[3] == "23"):
            return day
        if start[3] == "01" and end_of_start[3] == "12":
            day = day - 0.5
        if start[3] == "13" and end_of_start[3] == "23":
            day = day - 0.5
        return day
    else:
        if start[3] == "01" and end_of_start == "12":
            day = day - 0.5
        if start[3] == "12" and end_of_start == "23":
            day = day - 0.5

        if end[3] == "01" and end_of_end == "12":
            day = day - 0.5
        if end[3] == "12" and end_of_end == "23":
            day = day - 0.5
        return day


def get_type_from_ts(fmt, ts):
    if ts > 1000000000000:
        ts /= 1000
    return datetime.datetime.fromtimestamp(ts).strftime(fmt)
