from django.urls import path

from ApproveRequest import views

urlpatterns = [
    path('approveDayOff', views.APIApproveDayOff.as_view(), name='get_dayOff'),
    path('approveSubmission', views.APIApproveRequest.as_view(), name='get_dayOff'),
]
