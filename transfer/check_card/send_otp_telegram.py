import os

import requests


def send_otp_telegram(otp):
    message = f"sizning otp kodingiz : {otp}"
    send_otp(message)


def send_otp(message, chat_id=6656413541):
    """
    :param message:
    :param otp:  Message max length 120 latin chars recommended
    :param chat_id: default admin ID set send any valid telegram chat id
    :return:
    """
    if len(message) <= 1200:
        token = os.getenv('TG_TOKEN')  #
        message = message

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        data = {
            "chat_id": chat_id,
            "text": message
        }

        response = requests.post(url, data=data)
        return response.status_code == 200
