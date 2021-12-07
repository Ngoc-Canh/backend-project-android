from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from app_config import CHECK_IN, CHECK_OUT, INVALID_AREA, LIST_VALID_IP
from auths.models import User
from core.models import Submission, Holiday
from app_common import Timer
from core.service.notification import notify


def job_daily():
    current_date = Timer.get_time_now().date()
    previous_day = current_date - timezone.timedelta(days=1)
    if previous_day.weekday() == 0:
        previous_day = current_date - timezone.timedelta(days=3)
    user_data = apply_policy(previous_day)
    notify(user_data)
    return user_data


def apply_policy(current_date):
    day_str = f'{current_date.day}-{current_date.month}-{current_date.year}'
    dict_miss_event = {}

    if is_holiday(current_date):
        return

    users = User.objects.filter(is_active=True).exclude(email="bot@gmail.com")

    for user in users:
        if Timer.is_on_leave(event_time=current_date, user=user) and user.is_active:
            try:
                event_checkIn = user.event_set.get(event_type__event_name=CHECK_IN, created_date=current_date,
                                                   is_active=True)
                dict_miss_event[user.email] = {
                    day_str: {
                        CHECK_IN: False
                    }
                }
            except:
                event_checkIn = ""
                dict_miss_event[user.email] = {
                    day_str: {
                        CHECK_IN: True
                    }
                }

            try:
                event_checkOut = user.event_set.get(event_type__event_name=CHECK_OUT, created_date=current_date,
                                                    is_active=True)

                dict_miss_event[user.email][day_str].update({
                    CHECK_OUT: False
                })
            except:
                event_checkOut = None
                dict_miss_event[user.email][day_str].update({
                    CHECK_OUT: True
                })

            try:
                if event_checkIn:
                    if valid_area(event_checkIn.user_ip):
                        submission = Submission.get_or_create_submission(
                            **{"event": event_checkIn, "reason": INVALID_AREA}
                        )
                        submission.save()
            except Exception as e:
                print(e)

            try:
                if event_checkOut:
                    if valid_area(event_checkOut.user_ip):
                        submission = Submission.get_or_create_submission(
                            **{"event": event_checkOut, "reason": INVALID_AREA}
                        )
                        submission.save()
            except Exception as e:
                print(e)

    return dict_miss_event


def valid_area(ips):
    return ips in LIST_VALID_IP


def additional_day():
    for user in User.objects.filter(is_active=True):
        user.total_dayOff += 12
        user.save()


def scheduler_job_in_week():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_daily(), 'cron', year="*", month="*", hours=7, day_of_week="mon,tue,wed,thu,fri")
    scheduler.start()


def scheduler_job_every_new_year():
    schedule = BackgroundScheduler()
    schedule.add_job(additional_day, 'cron', year="*", month=1, day=1)
    schedule.start()


def is_holiday(date):
    for hld in Holiday.objects.filter():
        if hld.start_holiday <= date <= hld.end_holiday:
            return True
    return False
