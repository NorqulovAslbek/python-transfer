import requests


def send_otp_telegram(chat_id, otp):
    token = "6608269679:AAGM8vtudTooiUKpvQVyvlnCOAjV5vdFbBE"
    message = f"Sizning kodingiz: {otp}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=data)
    return response.status_code == 200
