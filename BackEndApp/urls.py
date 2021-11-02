from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('auth/', include('auths.urls')),
    path('approve/', include('ApproveRequest.urls')),
    path('', include('CheckInOut.urls')),
    path('submission/', include('submission.urls')),
    path('dayOff/', include('DayOff.urls')),
    path('holiday/', include('Holiday.urls')),
]
