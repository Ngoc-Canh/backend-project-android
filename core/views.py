from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# Valid IP_ADDRESS
import app_config
from app_common import Client


class ValidateIP(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        valid_status = False
        try:
            client_info = Client.get_client_info(request)
            user_ip = client_info['user_ip']
            VALIDATE_IPS = app_config.LIST_VALID_IP.split(',')

            if user_ip in VALIDATE_IPS:
                valid_status = True
        except Exception as e:
            pass

        return Response({'status': valid_status}, 200)
