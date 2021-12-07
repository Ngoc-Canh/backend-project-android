import json

import requests

from app_config import URL_NOTIFY, HEADER_NOTIFY, CHECK_OUT, CHECK_IN
from auths.models import User


def notify(data):
    for email, info in data.items():
        user = User.objects.filter(email=email).first()
        if not user.token_device:
            continue
        message = ""
        for day, event in info.items():
            if event[CHECK_IN] and event[CHECK_OUT]:
                message = f"Bạn quên chấm công cả ngày {day}"
                break
            if event[CHECK_IN]:
                message = f"Bạn quên chấm công lúc đến ngày {day}"
            if event[CHECK_OUT]:
                message = f"Bạn quên chấm công lúc về ngày {day}"

        body = {
            "to": f"{user.token_device}",
            "data": {
                "title": "Quên chấm công",
                "body": f"{message}"
            }
        }
        rs = requests.post(url=URL_NOTIFY, data=json.dumps(body), headers=HEADER_NOTIFY)
        print(rs.content)
