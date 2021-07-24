from django.urls import path

from auths import views
from rest_framework.authtoken import views as get_token

urlpatterns = [
    path('create_user', views.CreateAccountView.as_view(), name="create_user"),
    path('login', get_token.obtain_auth_token),
]
