import requests


def valyuta(amount, currency_code):
    valyuta_list = requests.get("https://cbu.uz/oz/arkhiv-kursov-valyut/json/").json()
    valyuta_obj = next((v for v in valyuta_list if v['Code'] == str(currency_code)), None)

    if not valyuta_obj:
        return "Valyuta topilmadi."

    rate = float(valyuta_obj['Rate'])
    converted = amount / rate
    return {
        "currency": valyuta_obj['Ccy'],
        "rate": rate,
        "converted_amount": round(converted, 2)
    }
