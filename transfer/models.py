from django.db import models


# Create your models here.
class TransferState(models.TextChoices):
    CREATED = "created", "Created"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"


class Transfer(models.Model):
    ext_id = models.CharField(max_length=100, unique=True)
    sender_card_number = models.CharField(max_length=16)
    sender_card_expiry = models.CharField(max_length=5)
    sender_phone = models.CharField(max_length=13)
    receiver_card_number = models.CharField(max_length=16)
    receiver_phone = models.CharField(max_length=13)
    sending_amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10)
    receiving_amount = models.DecimalField(max_digits=20, decimal_places=2)
    state = models.CharField(max_length=20,
                             choices=TransferState.choices,
                             default=TransferState.CREATED)
    try_count = models.IntegerField(default=0)
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ext_id}"

    def to_result(self):
        return {
            "ext_id": self.ext_id,
            "state": self.get_state_display()
        }
