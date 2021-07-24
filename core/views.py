from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from app_config import CHECK_IN, CHECK_OUT, LIST_VALID_IP
from app_common import Client, Timer
from core.models import Event


class ValidateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        valid_status = False
        try:
            client_info = Client.get_client_info(request)
            user_ip = client_info['user_ip']
            VALIDATE_IPS = LIST_VALID_IP.split(',')

            if user_ip in VALIDATE_IPS:
                valid_status = True
        except Exception as e:
            pass

        return Response({'status': valid_status}, 200)


class CheckInView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            client_info = Client.get_client_info(request)
            response_checkin = check_in_function(request.user, client_info)
            status_checkin = response_checkin.data['code']
            if status_checkin == 200:
                return Response({"chamcong": response_checkin.data['msg']}, status=status_checkin)
            else:
                return Response({"chamcong": response_checkin.data['msg']}, status=status_checkin)
        except Exception as e:
            return Response({'chamcong': {'status': "Error", 'msg': f"{str(e)}"}}, status=400)


class CheckOutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            client_info = Client.get_client_info(request)
            response_checkin = check_out_function(request.user, client_info)
            status_checkout = response_checkin.data['code']
            if status_checkout == 200:
                return Response({"chamcong": response_checkin.data['msg']}, status=status_checkout)
            else:
                return Response({"chamcong": response_checkin.data['msg']}, status=status_checkout)
        except Exception as e:
            return Response({'chamcong': {'status': "Error", 'msg': f"{str(e)}"}}, status=400)


class GetEventView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            events = Event.objects.filter(created_by=request.user, is_active=True, created_date=Timer.get_today())

            metadata = {
                'valid_ip': validate_ip(request),
                'user': {"full_name": request.user.full_name},
                'event': None
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
            events = Event.objects.filter(created_by=request.user, is_active=True)

            history_data = {
                'user': {"full_name": request.user.full_name},
                'event': None
            }

            for event in events:
                event_item = {
                    "created_at": event.created_at,
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


class CalendarView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        event = Event.objects.filter(created_date__month=request)


def check_in_function(user, info):
    try:
        event = Event.objects.filter(created_by=user, created_date=Timer.get_today(), is_active=True,
                                     event_type__event_name=CHECK_IN)

        if not event:
            info['created_by'] = user
            Event.create_check_in(**info)
            return Response({'code': 200, 'status': 'OK', 'msg': 'Check in thành công'})
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
            return Response({'code': 200, 'status': 'OK', 'msg': 'Check in thành công.'})
        else:
            return Response({'code': 400, 'status': "Error", 'msg': "Bạn chưa CheckIn. Nên không thể CheckOut."})
    except Exception as e:
        return Response({'code': 500, 'status': "Error", 'msg': f'{str(e)}'})


def validate_ip(request):
    client_info = Client.get_client_info(request)
    user_ip = client_info['user_ip']
    VALIDATE_IPS = LIST_VALID_IP.split(',')

    if user_ip in VALIDATE_IPS:
        return True
    else:
        return False
