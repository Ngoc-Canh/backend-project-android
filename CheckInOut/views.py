from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_common import Client, Timer
from app_config import CHECK_IN, CHECK_OUT
from core.models import Event


class CheckInView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            client_info = Client.get_client_info(request)
            response_checkin = check_in_function(request.user, client_info)
            status_checkin = response_checkin.data['code']
            if status_checkin == 200:
                return Response({"msg": response_checkin.data['msg']}, status=status_checkin)
            else:
                return Response({"msg": response_checkin.data['msg']}, status=status_checkin)
        except Exception as e:
            return Response({'msg': f"{str(e)}"}, status=400)


class CheckOutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            client_info = Client.get_client_info(request)
            response_checkin = check_out_function(request.user, client_info)
            status_checkout = response_checkin.data['code']
            if status_checkout == 200:
                return Response({"msg": response_checkin.data['msg']}, status=status_checkout)
            else:
                return Response({"msg": response_checkin.data['msg']}, status=status_checkout)
        except Exception as e:
            return Response({'msg': f"{str(e)}"}, status=400)


def check_in_function(user, info):
    try:
        event = Event.objects.filter(created_by=user, created_date=Timer.get_today(), is_active=True,
                                     event_type__event_name=CHECK_IN)

        if not event:
            info['created_by'] = user
            Event.create_check_in(**info)
            return Response({'code': 200, 'status': 'OK', 'msg': 'Chấm công lúc đến thành công'})
        else:
            return Response({'code': 400, 'status': "Error", 'msg': "Đã Checkin. Không thể checkin lại. "})
    except Exception as e:
        return Response({'code': 500, 'status': "Error", 'msg': f'{str(e)}'})


def check_out_function(user, info):
    try:
        event_filter = Event.objects.filter(created_by=user, created_date=Timer.get_today(),
                                            is_active=True)

        event_checkIn = event_filter.filter(event_type__event_name=CHECK_IN)

        if event_checkIn:
            event_checkOut = event_filter.filter(event_type__event_name=CHECK_OUT)
            if event_checkOut:
                return Response({'code': 400, 'status': "Error", 'msg': "Bạn đã CheckOut. Nên không thể CheckOut lại."})
            info['created_by'] = user
            Event.create_check_out(**info)
            return Response({'code': 200, 'status': 'OK', 'msg': 'Chấm công lúc về thành công.'})
        else:
            return Response({'code': 400, 'status': "Error", 'msg': "Bạn chưa CheckIn. Nên không thể CheckOut."})
    except Exception as e:
        return Response({'code': 500, 'status': "Error", 'msg': f'{str(e)}'})
