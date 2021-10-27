from django.urls import path

from submission import views

urlpatterns = [
    path('', views.ListSubmission.as_view()),
    path('<int:pk>', views.ListSubmission.as_view())
]
