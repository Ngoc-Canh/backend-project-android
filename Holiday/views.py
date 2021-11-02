from datetime import datetime

from dateutil import parser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Holiday


class APIHoliday(APIView):
    permission_class = (IsAuthenticated,)

    def get(self, request):
        if request.user.is_admin:
            result = {
                'data': []
            }

            data = Holiday.objects.all().order_by("-start_holiday")

            for hld in data:
                items = {
                    "id": hld.id,
                    "startDate": hld.start_holiday,
                    "endDate": hld.end_holiday,
                    "title": hld.description,
                    "numberDay": hld.sum_day
                }
                result['data'].append(items)

            return Response(result, status=200)
        else:
            return Response({'msg': 'Bạn không có quyền truy cập'}, status=500)

    def post(self, request):
        try:
            if request.user.is_admin:
                start_date = parser.parse(request.data["startDate"])
                end_date = parser.parse(request.data["endDate"])
                if start_date < end_date:
                    return Response({'msg': 'Ngày bắt đầu không thể lớn hơn ngày kết thúc.'}, status=500)

                sum_day = start_date - end_date
                request.data["sum_day"] = sum_day.days + 1
                request.data["startDate"] = start_date
                request.data["endDate"] = end_date
                Holiday.create_holiday(**request.data)
                return Response({'msg': 'Thêm mới thành công'}, status=202)
            else:
                return Response({'msg': 'Bạn không có quyền truy cập'}, status=500)
        except Exception as e:
            return Response({"msg": f"{str(e)}"}, status=500)

    def delete(self, request, pk):
        try:
            if request.user.is_admin:
                Holiday.objects.filter(id=pk).delete()
                return Response({'msg': 'Xóa bản ghi thành công'}, status=200)
            else:
                return Response({'msg': 'Bạn không có quyền truy cập'}, status=500)
        except Exception as e:
            return Response({"msg": f"{str(e)}"}, status=500)
