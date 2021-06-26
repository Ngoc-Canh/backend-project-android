from django.contrib import admin

from core.models import *

admin.site.register(Event)
admin.site.register(DayOff)
admin.site.register(Reason)
admin.site.register(Submission)
admin.site.register(DayOffType)
admin.site.register(StatusType)
admin.site.register(EventType)
