from django.conf.urls import url
from django.urls import path

from core import views

urlpatterns = [
    # url(r'^api-token-auth/', views.obtain_auth_token),
    path('hello/', views.HelloView.as_view(), name='hello'),
]
