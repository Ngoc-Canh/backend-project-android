from django.urls import path

from Holiday import views

urlpatterns = [
    path('', views.APIHoliday.as_view()),
    path('<int:pk>', views.APIHoliday.as_view())
]
