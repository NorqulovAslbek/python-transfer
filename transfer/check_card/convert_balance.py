import requests


def valyuta(amount, currency_code):
    if currency_code == 860:
        return amount
    valyuta_list = requests.get("https://cbu.uz/oz/arkhiv-kursov-valyut/json/").json()
    valyuta_obj = next((v for v in valyuta_list if v['Code'] == str(currency_code)), None)

    if not valyuta_obj:
        return "Valyuta topilmadi."

    rate = float(valyuta_obj['Rate'])
    converted = amount / rate
    return converted


def convert_rub_to_uzs(amount):
    valyuta_list = requests.get("https://cbu.uz/oz/arkhiv-kursov-valyut/json/").json()
    valyuta_obj = next((v for v in valyuta_list if v['Code'] == str(643)), None)
    if not valyuta_obj:
        return "Valyuta topilmadi."

    rate = (valyuta_obj['Rate'])
    converted = float(amount) * float(rate)
    return converted
