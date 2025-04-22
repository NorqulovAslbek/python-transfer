from django.contrib import admin
from .models import Transfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        'ext_id', 'sender_card_number', 'sending_amount', 'receiver_card_number', 'receiving_amount', 'state',
        "created_at")
    readonly_fields = ("created_at_formatted",)

    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    created_at_formatted.short_description = "Created At"
