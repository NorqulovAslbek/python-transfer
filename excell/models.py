from django.db import models


# Create your models here.
class Card(models.Model):
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expire = models.CharField(max_length=5, null=True, blank=True)
    phone = models.CharField(max_length=13, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)  # ENUM bolishi kerak edi
    balance = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)

    # declined = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.card_number}"

    def card_result(self):
        return {
            "card_number": f"{self.card_number[:4]}****{self.card_number[-4:]}",
            "expire": self.expire,
            "balance": float(self.balance),
            "status": self.status
        }
