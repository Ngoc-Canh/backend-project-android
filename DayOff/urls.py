from django.urls import path

from DayOff import views

urlpatterns = [
    # GET, POST
    path('', views.ListDayOff.as_view()),

    # DELETE
    path('<int:pk>', views.ListDayOff.as_view())
]
