import datetime

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_common import Timer
from app_config import STATUS_WAITING, CHECK_OUT, CHECK_IN
from core.models import Submission, Event, DayOff, Holiday


class ListSubmission(APIView):
    permission_class = (IsAuthenticated,)

    def get(self, request):
        submissions = Submission.objects.filter(is_active=True, event__created_by=request.user)
        data = {
            "event": []
        }
        for submission in submissions:
            submission_item = {
                "id": submission.id,
                "created_by": submission.event.created_by.full_name,
                "created_at": submission.event.created_at,
                "event_type": submission.event.event_type.get_event_name_display(),
                "reason": ", ".join(sub.name for sub in submission.reason_many.all()),
                "created_date": datetime.datetime.fromtimestamp(submission.created_at).date(),
                "manager_confirm": submission.manager_confirm.code,
                "status": True if submission.manager_confirm.code == STATUS_WAITING else False
            }
            data['event'].append(submission_item)

        return Response(data, status=200)

    def post(self, request):
        try:
            result = submission_function(request.user, request.data)
            if result.data['code'] == 200:
                return Response({"msg": result.data['msg']}, status=result.data['code'])
            else:
                return Response({"msg": result.data['msg']}, status=result.data['code'])
        except Exception as e:
            return Response({'msg': f"{str(e)}"}, status=400)

    def delete(self, request, pk):
        try:
            submission = Submission.objects.get(id=pk, event__created_by=request.user)
            if submission:
                return Response({"msg": "Không tồn tại bản ghi."}, status=400)

            submission.is_active = False
            submission.event.is_active = False
            submission.save()
            return Response({"msg: Hủy bỏ yêu cầu thành công"}, status=200)
        except Exception as e:
            return Response({f"msg: {str(e)}"}, status=400)


def submission_function(user, data):
    try:
        convert_date = datetime.datetime.strptime(f"{data['created_date']['year']}/{data['created_date']['month']}/"
                                                  f"{data['created_date']['day']}", "%Y/%m/%d").date()

        data['created_by'] = user
        data_event = {
            "created_by": user,
            "created_at": data['created_at'],
            "created_date": convert_date
        }

        if Timer.is_holiday(convert_date):
            return Response({'code': 500, 'status': "Error", 'msg': "Không thể tạo yêu cầu trùng ngày nghỉ lễ"})

        if convert_date > Timer.get_time_now().date():
            return Response({'code': 500, 'status': "Error", 'msg': "Không thể chấm bù cho tương lai"})

        if convert_date.weekday() >= 5:
            return Response({'code': 500, 'status': "Error", 'msg': "Không thể chấm công vào cuối tuần"})

        if Timer.is_day_off(user, convert_date):
            return Response({'code': 500, 'status': "Error", 'msg': "Không thể tạo yêu cầu chấm bù khi đang trong "
                                                                    "ngày nghỉ"})

        event = Event.objects.filter(created_date=convert_date,
                                     created_by=user,
                                     event_type__event_name=data['event_type'], is_active=True)
        if not event:
            if data['event_type'] == CHECK_OUT:
                event = Event.create_check_out(**data_event)
            if data['event_type'] == CHECK_IN:
                event = Event.create_check_in(**data_event)

            data['event'] = event
            Submission.create_submission(**data)
        else:
            return Response({'code': 500, 'status': "Error", 'msg': "Đã có sự kiện chấm công trước đó, "
                                                                    "vui lòng kiểm tra lại"})

        return Response({'code': 200, 'status': 'OK', 'msg': 'Tạo mới thành công'})
    except Exception as e:
        return Response({'code': 500, 'status': "Error", 'msg': f'{str(e)}'})
