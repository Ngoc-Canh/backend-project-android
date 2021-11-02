from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_config import STATUS_ACCEPT, STATUS_DECLINE, PAID_LEAVE
from auths.models import Role, User
from core.models import Submission, StatusType, DayOff, DayOffType


# API duyet cong
class APIApproveRequest(APIView):
    permission_class = (IsAuthenticated, )

    def get(self, request):
        # Lay ra danh sach cac request
        if request.user.is_active and Role.objects.get(name="manager") in request.user.roles.all():
            result = {
                'submission_list': []
            }
            submissions = Submission.objects.filter(
                event__created_by__manager__email=request.user.email, is_active=True).order_by("manager_confirm")
            for sub in submissions:
                item = {
                    "id": sub.id,
                    "created_by": sub.event.created_by.full_name,
                    "created_date": sub.event.created_date,
                    "type": sub.event.event_type.event_name,
                    "reason": ", ".join(i.name for i in sub.reason_many.all()),
                    "created_at": sub.event.created_at,
                    "status": True if sub.manager_confirm.code == "waiting" else False,
                    "manager_confirm": sub.manager_confirm.name
                }
                result["submission_list"].append(item)
            return Response(data=result, status=200)
        else:
            return Response({'msg': 'Bạn không có quyền truy cập'}, status=500)

    def post(self, request):
        # Phe Duyet cong
        list_submission = request.data['list_submission']
        for submission in list_submission:
            try:
                sub = Submission.objects.get(id=submission.id)
                if not sub.is_active:
                    break
                status = StatusType.objects.filter(code=request.data['status']).first()
                sub.manager_confirm = status
                sub.save()
            except Exception as e:
                return Response({"msg": f"{str(e)}"}, status=500)
        return Response({"msg": "Duyệt yêu cầu hoàn tất"}, status=200)


# API duyet ngay nghi phep
class APIApproveDayOff(APIView):
    permission_class = (IsAuthenticated,)

    def get(self, request):
        # Tra ve danh sach cac yeu cau nghi phep or khong phep
        if request.user.is_active and Role.objects.get(name="manager") in request.user.roles.all():
            dayOff = DayOff.objects.filter(created_by__manager__email=request.user.email, is_active=True)\
                .order_by("manager_confirm")
            result = {
                "data": []
            }
            for df in dayOff:
                item = {
                    "id": df.id,
                    "created_by": df.created_by.email,
                    "manager_confirm": df.manager_confirm.name,
                    "manager_confirm_code": True if df.manager_confirm.code == "waiting" else False,
                    "start_date": df.start_date,
                    "end_date": df.end_date,
                    "total_dayOff": df.number_day_off,
                    "type": ", ".join(i.name for i in df.type_off.all()),
                    "type_code": ", ".join(i.code for i in df.type_off.all()),
                    "status": df.is_active
                }
                result['data'].append(item)
            return Response(data=result, status=200)
        else:
            return Response({'code': 500, 'status': 'NOK', 'msg': 'Bạn không có quyền truy cập'})

    def post(self, request):
        try:
            dict_result = {}
            list_day_off = request.data['data']
            for day in list_day_off:
                if f'{day["created_by"]}' not in dict_result.keys():
                    dict_result[f'{day["created_by"]}'] = [day]
                else:
                    dict_result[f"{day['created_by']}"].append(day)

            for email, data in dict_result.items():
                user = User.objects.get(email=email)
                for detail in data:
                    type_off = DayOffType.objects.get(code=detail["type_code"])
                    if detail["total_dayOff"] > user.total_dayOff and type_off.code is PAID_LEAVE:
                        return Response({"code": 500, "msg": f"Số ngày phép của {user.full_name} không đủ để kiểm duyệt"})
                    user.total_dayOff -= detail["total_dayOff"]
                user.save()

            approve = request.query_params['accept']

            managerConfirm = StatusType.objects.get(code=STATUS_ACCEPT)
            if not approve:
                managerConfirm = StatusType.objects.get(code=STATUS_DECLINE)

            for dayOff in list_day_off:
                obj = DayOff.objects.get(id=dayOff['id'])
                obj.manager_confirm = managerConfirm
                obj.save()

            return Response({"code": 200, "msg": "Duyệt yêu cầu hoàn tất"})
        except Exception as e:
            return Response({"code": 500, "msg": f"{e}"})
