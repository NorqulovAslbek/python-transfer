import json

import requests


# from django.utils.text import phone2numeric
#
#
# def auth(email, password):
#     url = 'notify.eskiz.uz/api/auth/login'
#     data = json.dumps({
#         "email": "aslbeknorqulov246@gmail.com",  # email
#         "password": "u3ueQ6Z49FtKoStyPz6QYEKQam7ckiVlRJY06xUb"  # password
#     })
#     response = requests.post(url, data=data).json()
#     return response
#

def send_sms(balance, number):
    url = "https://notify.eskiz.uz/api/message/sms/send"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDcyMzc0MjQsImlhdCI6MTc0NDY0NTQyNCwicm9sZSI6InRlc3QiLCJzaWduIjoiNWJjYzcyYjIyMmU4NDczYjY4NzQ2ZDcxMjRkOTMzMjQ3NTgxMWE5NGQwNGE2YzQ5MzUwNzI4YjZiY2I3Y2Q1OCIsInN1YiI6IjYzMjIifQ.OBqrZvFDpO5NXCQwflzNCM94wagNGYCHuhswqzDMupM"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    if number != "None":
        message = f"{number} egasi sizning hisobingizda {balance} qoldi."
        print(f"???????????????????????????????   {number.replace("+", "")}")
        data = {
            "mobile_phone": f"{number.replace("+", "")}",
            "message": "Bu Eskiz dan test",
            "from": 4546,
            "callback_url": "http://0000.uz/test.php"
        }

        response = requests.post(url, data=data, headers=headers)
        return response.json()
