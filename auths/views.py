from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auths.models import User


class CreateAccountView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.user.is_admin:
            try:
                User.create_user(**request.data)
                return Response({'user': {'status': "success", 'msg': f"Thêm mới User thành công"}}, status=200)
            except Exception as e:
                return Response({'user': {'status': "Error", 'msg': f"{str(e)}"}}, status=400)
        else:
            return Response({'user': {'status': "Error", 'msg': "Bạn không có quyền truy cập"}}, status=400)


