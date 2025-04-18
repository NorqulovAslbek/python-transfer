from django.contrib import admin

from transfer.models import Transfer


# Register your models here.


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('ext_id', 'sender_card_number', 'sending_amount', 'receiver_card_number', 'receiving_amount')
