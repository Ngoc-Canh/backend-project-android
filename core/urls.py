from django.urls import path

from core import views

urlpatterns = [
    path('validate/', views.ValidateIP.as_view(), name='validate'),
]
