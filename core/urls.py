from django.urls import path

from core import views

urlpatterns = [
    path('job_daily/', views.ValidateView.as_view()),
    path('event/', views.GetEventView.as_view()),
    path('history', views.HistoryView.as_view()),
    path('saveTokenDevice', views.SaveDeviceToken.as_view()),
]
