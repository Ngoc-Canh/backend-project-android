from django.urls import path

from core import views

urlpatterns = [
    path('validate/', views.ValidateView.as_view(), name='validate'),
    path('checkin/', views.CheckInView.as_view(), name='checkin'),
    path('checkout/', views.CheckOutView.as_view(), name='checkin'),
    path('event/', views.GetEventView.as_view(), name='get_event'),
    path('history/', views.HistoryView.as_view(), name='get_event'),
]
