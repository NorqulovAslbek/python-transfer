import re
from datetime import datetime

from rest_framework import serializers


class CardSerializers(serializers.Serializer):
    card_number = serializers.CharField(max_length=16)
    phone = serializers.CharField(max_length=13)
    expiry = serializers.CharField(max_length=5)

    def validate_card_number(self, value):
        if not re.fullmatch(r'^\d{16}', value):
            raise serializers.ValidationError("the card has no 16 digits!")
        return value

    def validate_phone(self, value):
        if not re.fullmatch(r'\+998\d{9}', value):
            raise serializers.ValidationError("the phone number is not given in the correct format!")
        return value

    def validate_expiry(self, value):
        if not re.fullmatch(r'^(0[1-9]|1[0-2])/(\d{2})$', value):
            raise serializers.ValidationError("Invalid card expiration date format. Use MM/YY.")
        month, year = map(int, value.split('/'))
        now = datetime.now()
        current_year = now.year % 100
        current_month = now.month
        if year < current_year or (year == current_year and month < current_month):
            raise serializers.ValidationError("The card has already expired.")
        return value
