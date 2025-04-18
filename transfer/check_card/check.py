from datetime import datetime


def is_card_expired(exp_date_str):
    # "11/30" => MM/YY
    exp_month, exp_year = map(int, exp_date_str.split('/'))
    exp_year += 2000  # 30 => 2030

    # Expiry ni o'sha oy tugagan kun deb hisoblaymiz, ya'ni keyingi oy boshidan 1 kun oldin
    if exp_month == 12:
        exp_date = datetime(exp_year + 1, 1, 1)
    else:
        exp_date = datetime(exp_year, exp_month + 1, 1)

    # Hozirgi vaqt
    now = datetime.now()

    # Agar hozirgi vaqt expiry'dan keyin bo‘lsa — expired
    return now >= exp_date

# print(is_card_expired("11/23"))