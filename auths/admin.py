from django.contrib import admin

from auths.models import User, Role

admin.site.register(User)
admin.site.register(Role)
