from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
from rest_framework.response import Response


class Role(models.Model):
    ROLES = (
        ("user", "User"),
        ("manager", "Manager"),
        ("admin", "Administrator"),
        ("bot", "Bot"),
    )
    name = models.CharField(choices=ROLES, max_length=10)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=128)
    roles = models.ManyToManyField(Role)
    manager = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    total_dayOff = models.FloatField(default=0)

    def is_administrator(self):
        return self.roles.filter(name="admin")

    @classmethod
    def create_user(cls, **kwargs):
        try:
            user = User()
            user.email = kwargs['email']
            user.username = kwargs['full_name']
            user.full_name = kwargs['full_name']
            user.save()

            if kwargs['roles']:
                for role in kwargs['roles']:
                    get_role = Role.objects.filter(name=role).first()
                    user.roles.add(get_role)
            else:
                get_role = Role.objects.filter(name=Role.ROLES[0][0]).first()
                user.roles.add(get_role)

            user.save()
            return user
        except IntegrityError as e:
            if str(e) == "UNIQUE constraint failed: auths_user.email":
                raise IntegrityError("Thêm mới thất bại. Do email đã tồn tại.")
            else:
                raise IndentationError(f"{str(e)}")



