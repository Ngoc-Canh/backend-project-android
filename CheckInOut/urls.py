from django.urls import path

from CheckInOut import views

urlpatterns = [
    path('checkin/', views.CheckInView.as_view()),
    path('checkout/', views.CheckOutView.as_view())
]
