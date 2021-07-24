from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from app_common import Timer
from auths.models import User


class EventType(models.Model):
    EVENTS = (
        ("check_in", "Check In"),
        ("check_out", "Check Out")
    )
    event_name = models.CharField(choices=EVENTS, max_length=10)

    def __str__(self):
        return self.event_name


class Event(models.Model):
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.IntegerField()
    created_date = models.DateField()
    user_ip = models.CharField(default="127.0.0.1", max_length=20)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create_check_in(cls, **kwargs):
        created_date = Timer.get_today() if 'created_date' not in kwargs else kwargs['created_date']
        created_time = Timer.get_timestamp_now() if 'created_at' not in kwargs else kwargs['created_at']

        check_in_event = EventType.objects.get(event_name=EventType.EVENTS[0][0])

        try:
            event = Event.objects.get(created_by=kwargs['created_by'], created_date=created_date,
                                      event_type=check_in_event, is_active=True)
        except models.ObjectDoesNotExist:
            kwargs['created_date'] = created_date
            kwargs['event_type'] = check_in_event
            kwargs['created_at'] = created_time
            event = Event.objects.create(**kwargs)
        return event

    @classmethod
    def create_check_out(cls, **kwargs):
        created_date = Timer.get_today() if 'created_date' not in kwargs else kwargs['created_date']
        created_time = Timer.get_timestamp_now() if 'created_at' not in kwargs else kwargs['created_at']

        check_out_event = EventType.objects.get(event_name=EventType.EVENTS[0][1])

        try:
            event = Event.objects.get(created_by=kwargs['created_by'], created_date=created_date,
                                      event_type=check_out_event, is_active=True)
        except models.ObjectDoesNotExist:
            kwargs['created_date'] = created_date
            kwargs['event_type'] = check_out_event
            kwargs['created_at'] = created_time
            event = Event.objects.create(**kwargs)
        return event


class StatusType(models.Model):
    code = models.CharField(max_length=25)
    name = models.CharField(max_length=192, default=None)

    def __str__(self):
        return self.name


class Reason(models.Model):
    code = models.CharField(max_length=25)
    name = models.CharField(max_length=192)

    def __str__(self):
        return self.name


class Submission(models.Model):
    reason_many = models.ManyToManyField(Reason, related_name="new_reason", default=None, blank=True, null=True)
    created_at = models.IntegerField()
    last_update = models.IntegerField()
    manager_confirm = models.ForeignKey(StatusType, on_delete=models.CASCADE, default=None, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    another_reason = models.TextField()
    is_active = models.BooleanField(default=True)


class DayOffType(models.Model):
    code = models.CharField(max_length=25)
    name = models.CharField(max_length=192, default=None)

    def __str__(self):
        return self.name


class DayOff(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    number_day_off = models.FloatField()
    type_off = models.ForeignKey(DayOffType, on_delete=models.CASCADE, null=True, default=None, blank=True)
    another_reason = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_update = models.IntegerField()
    manager_confirm = models.ForeignKey(StatusType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
