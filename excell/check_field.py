import re


def check_card(card_number):
    empty = ""
    for num in card_number:
        if num.isdigit():
            empty += num
    return empty if len(empty) == 16 else "None"


def check_expire(date_str):
    date_str = date_str.strip()

    patterns = [
        r'^(\d{2})[-/.](\d{4})$',  # MM-YYYY or MM.YYYY or MM/YYYY
        r'^(\d{4})[-/.](\d{2})$',  # YYYY-MM or YYYY/MM
        r'^(\d{2})[-/.](\d{2})$',  # MM-YY or MM/YY
        r'^(\d{2})[-/.](\d{2})[-/.](\d{2,4})$',  # DD-MM-YY(YY)
        r'^(\d{2})[-/.](\d{4})$',  # DD-YYYY
        r'^(\d{2})[-/.](\d{2,4})$'  # fallback: e.g. 20.2024
    ]

    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            groups = list(map(int, match.groups()))
            if len(groups) == 2:
                if groups[0] > 12:
                    month = groups[1]
                    year = groups[0]
                else:
                    month = groups[0]
                    year = groups[1]
            elif len(groups) == 3:
                _, month, year = groups
            else:
                continue

            if not (1 <= month <= 12):
                return None

            if year < 100:
                year += 2000

            return f"{month:02}/{str(year)[-2:]}"

    return "None"


def check_phone(phone):
    """998 99 1205577  991205577"""
    empty = ""
    for p in phone:
        if p.isdigit():
            empty += p
    if len(empty) == 9:
        return f"+998{empty}"
    elif len(empty) == 12:
        return f"+{empty}"
    return "None"


def check_status(status):
    st = ["active", "expired", "inactive"]
    empty = ""
    for s in status:
        if s.isalpha():
            empty += s
    if empty.lower() in st:
        return empty.lower()
    return "None"


def clean_balance_for_bigint(balance_str):
    try:
        cleaned = str(balance_str).replace(",", "").replace(" ", "").strip()
        if cleaned.isdigit():
            return int(cleaned)
        return 0
    except (ValueError, TypeError):
        return 0
