from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auths.models import User, Role


class AccountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        is_hr = request.user.is_admin
        if is_hr:
            data = User.objects.exclude(email="bot@gmail.com")
            result = {
                "list_user": []
            }

            for rs in data:
                is_user = False
                is_manager = False
                for role in rs.roles.all():
                    if "user" in role.name:
                        is_user = True
                    if "manager" in role.name:
                        is_manager = True
                item = {
                    "id": rs.id,
                    "email": rs.email,
                    "full_name": rs.full_name,
                    "manager_email": rs.manager.email if rs.manager else "",
                    "manager_name": rs.manager.full_name if rs.manager else "",
                    "is_active": rs.is_active,
                    "is_admin": rs.is_admin,
                    "is_user": is_user,
                    "is_manager": is_manager,
                    "dayOff": rs.total_dayOff
                }
                result['list_user'].append(item)
            return Response(result, status=200)
        return Response({'code': 404, 'status': 'NOK', 'msg': 'Bạn không có quyền truy cập'})

    def post(self, request):
        if request.user.is_admin:
            try:
                role = Role.objects.all()
                arrRole = []
                if request.data['is_user']:
                    ft_role = role.filter(name="user").first()
                    arrRole.append(ft_role.name)
                if request.data["is_manager"]:
                    ft_manager = role.filter(name="manager").first()
                    ft_user = role.filter(name="user").first()
                    arrRole.append(ft_manager.name)
                    arrRole.append(ft_user.name)
                request.data['roles'] = arrRole
                User.create_user(**request.data)
                return Response({'msg': f"Thêm mới User thành công"}, status=201)
            except Exception as e:
                return Response({'msg': f"{str(e)}"}, status=400)
        else:
            return Response({'msg': "Bạn không có quyền truy cập"}, status=401)


class InfoView(APIView):
    permission_class = (IsAuthenticated, )

    def get(self, request):
        try:
            user = request.user
            roles = user.roles.all()
            is_user = False
            is_manager = False
            for role in roles:
                if "user" in role.name:
                    is_user = True
                if "manager" in role.name:
                    is_manager = True
            data = {
                "full_name": user.full_name,
                "manager_email": user.manager.email if user.manager else "",
                "manager_name": user.manager.full_name if user.manager else "",
                "dayOff": user.total_dayOff,
                "email": user.email,
                "is_admin": user.is_admin,
                "is_user": is_user,
                "is_manager": is_manager,
                "is_active": user.is_active,
                "token": str(user.auth_token)
            }
            return Response(status=200, data=data)
        except Exception as e:
            return Response({"status": "Error", "msg": f"{str(e)}"}, status=400)
