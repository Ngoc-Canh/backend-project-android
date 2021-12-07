from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from app_common import Timer
from app_config import CHECK_IN, CHECK_OUT, STATUS_WAITING, INVALID_FORGOT_CHECK, STATUS_CANCEL, OTHER_REASON
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

    def __str__(self):
        return f"{self.created_by} - {self.created_date}"

    @classmethod
    def create_check_in(cls, **kwargs):
        created_date = Timer.get_today() if 'created_date' not in kwargs else kwargs['created_date']
        created_time = Timer.get_timestamp_now() if 'created_at' not in kwargs else kwargs['created_at']

        check_in_event = EventType.objects.get(event_name=EventType.EVENTS[0][0])
        user_ip = "127.0.0.1" if 'user_ip' not in kwargs else kwargs['user_ip']

        try:
            event = Event.objects.get(created_by=kwargs['created_by'], created_date=created_date,
                                      event_type=check_in_event, is_active=True)
        except models.ObjectDoesNotExist:
            kwargs['created_date'] = created_date
            kwargs['event_type'] = check_in_event
            kwargs['created_at'] = created_time
            kwargs['user_ip'] = user_ip
            event = Event.objects.create(**kwargs)
        return event

    @classmethod
    def create_check_out(cls, **kwargs):
        created_date = Timer.get_today() if 'created_date' not in kwargs else kwargs['created_date']
        created_time = Timer.get_timestamp_now() if 'created_at' not in kwargs else kwargs['created_at']

        check_out_event = EventType.objects.get(event_name=EventType.EVENTS[1][0])
        user_ip = "127.0.0.1" if 'user_ip' not in kwargs else kwargs['user_ip']

        try:
            event = Event.objects.get(created_by=kwargs['created_by'], created_date=created_date,
                                      event_type=check_out_event, is_active=True)
        except models.ObjectDoesNotExist:
            kwargs['created_date'] = created_date
            kwargs['event_type'] = check_out_event
            kwargs['created_at'] = created_time
            kwargs['user_ip'] = user_ip
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
    created_at = models.IntegerField(default=0)
    last_update = models.IntegerField(default=0)
    manager_confirm = models.ForeignKey(StatusType, on_delete=models.CASCADE, default=None, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    another_reason = models.TextField(default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_or_create_submission(cls, **kwargs):
        try:
            submission = Submission.objects.filter(event=kwargs['event'], is_active=True)
            if not submission:
                raise models.ObjectDoesNotExist
            if "reason" in kwargs:
                reason = Reason.objects.filter(code=kwargs['reason']).first()
                submission.reason_many.add(reason)

        except models.ObjectDoesNotExist:
            manager_confirm = StatusType.objects.filter(code=STATUS_WAITING)
            reason = Reason.objects.filter(code=kwargs['reason']).first()
            submission = Submission.objects.create(
                event=kwargs['event'],
                created_at=Timer.get_timestamp_now(),
                last_update=Timer.get_timestamp_now(),
                manager_confirm=manager_confirm
            )
            submission.reason_many.add(reason)
        return submission

    @classmethod
    def create_submission(cls, **kwargs):
        try:
            submission = Submission.objects.get(event=kwargs['event'], is_active=True)
            if 'reason' in kwargs:
                reason = Reason.objects.filter(code=kwargs['reason'])
                submission.reason_many.add(reason)
            if submission.manager_confirm.code == STATUS_CANCEL:
                raise models.ObjectDoesNotExist
        except Exception as e:
            manager_confirm = StatusType.objects.get(code=STATUS_WAITING)
            reason = Reason.objects.filter(code=kwargs['reason']).first()

            submission = Submission.objects.create(
                event=kwargs['event'],
                created_at=Timer.get_timestamp_now(),
                last_update=Timer.get_timestamp_now(),
                manager_confirm=manager_confirm
            )
            submission.reason_many.add(reason)

        return submission

    def __str__(self):
        return f"{self.event.created_by} - {self.event.created_date}"


class DayOffType(models.Model):
    code = models.CharField(max_length=25)
    name = models.CharField(max_length=192, default=None)

    def __str__(self):
        return self.name


class DayOff(models.Model):
    ts_start_for_start_date = models.IntegerField(default=0)
    ts_end_for_start_date = models.IntegerField(default=0)
    ts_start_for_end_date = models.IntegerField(default=0)
    ts_end_for_end_date = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    number_day_off = models.FloatField()
    type_off = models.ManyToManyField(DayOffType, null=True, default=None, blank=True)
    another_reason = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_update = models.IntegerField()
    manager_confirm = models.ForeignKey(StatusType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.created_by}: {self.start_date}-{self.end_date}"

    @classmethod
    def create_day_off(cls, **kwargs):
        try:
            manager_confirm = StatusType.objects.get(code=STATUS_WAITING)
            typeOff = DayOffType.objects.filter(code=kwargs['type_off']).first()

            day_off = DayOff.objects.create(
                ts_start_for_start_date=kwargs["ts_start_for_start_date"],
                ts_end_for_start_date=kwargs["ts_end_for_start_date"],
                ts_start_for_end_date=kwargs["ts_start_for_end_date"],
                ts_end_for_end_date=kwargs["ts_end_for_end_date"],
                start_date=kwargs["start_date"],
                end_date=kwargs["end_date"],
                number_day_off=kwargs['number_day_off'],
                created_by=kwargs["created_by"],
                manager_confirm=manager_confirm,
                last_update=Timer.get_timestamp_now()
            )

            day_off.type_off.add(typeOff)
            return day_off
        except Exception as e:
            raise e


class Holiday(models.Model):
    start_holiday = models.DateField()
    end_holiday = models.DateField()
    sum_day = models.IntegerField()
    description = models.CharField(max_length=192, default=None, null=True, blank=True)

    @classmethod
    def create_holiday(cls, **kwargs):
        try:
            start_holiday = kwargs['startDate']
            end_holiday = kwargs['endDate']
            description = kwargs['title']
            holiday = Holiday.objects.create(
                start_holiday=start_holiday,
                end_holiday=end_holiday,
                description=description,
                sum_day=kwargs["sum_day"]
            )
            return holiday
        except Exception as e:
            raise e


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
