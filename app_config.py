LIST_VALID_IP = "127.0.0.1, 14.180.45.99, 113.167.109.251"

CHECK_IN = "check_in"
CHECK_OUT = "check_out"

STATUS_WAITING = "waiting"
STATUS_ACCEPT = "accept"
STATUS_DECLINE = "decline"
STATUS_CANCEL = "cancel"

MORNING_SHIFT = "morning"
AFTERNOON = "afternoon"
ALL_DAY = "all_day"

PAID_LEAVE = "paid_leave"
UNPAID_LEAVE = "unpaid_leave"

INVALID_FORGOT_CHECK = "invalid_forgot_check"
INVALID_AREA = "invalid_area"
OTHER_REASON = "other"

SERVER_KEYS = "key=AAAApWhXbSY:APA91bGHvG_pkRxpcIMJu2eYk6zRdKYN95tZkRIjFq6pC2P2xQiHt6ejYcFT7Hsx8jdXxIJxXZoCLye5-" \
              "KQrvVja0F9RnIO0pPflrNHP91Ub0lbf3lztJAhbyjRD65wPdu5U04W5x-ho"

URL_NOTIFY = "https://fcm.googleapis.com/fcm/send"

HEADER_NOTIFY = {
    "Content-Type": "application/json",
    "Authorization": SERVER_KEYS
}
