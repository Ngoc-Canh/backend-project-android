import json

import requests

from app_config import URL_NOTIFY, HEADER_NOTIFY, CHECK_OUT, CHECK_IN


def notify(data):
    with open('device_token.json', 'r') as openfile:
        listObj = json.load(openfile)

    for email, info in data.items():
        try:
            tokenDevice = [i[email]["token_device"] for i in listObj][0]
        except:
            break

        if not tokenDevice:
            break
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
            "to": f"{tokenDevice}",
            "data": {
                "title": "Quên chấm công",
                "body": f"{message}"
            }
        }
        rs = requests.post(url=URL_NOTIFY, data=json.dumps(body), headers=HEADER_NOTIFY)
        print(rs.status_code)
