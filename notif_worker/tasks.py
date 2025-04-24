from celery import shared_task

from excell.models import Card
from transfer.check_card.send_otp_telegram import send_otp
from transfer.models import Transfer


@shared_task
def send_daily_report():
    total_cards = Card.objects.count()
    total_transfers = Transfer.objects.count()
    message = f"📊 Daily Report:\n\n🪪 Total Cards: {total_cards}\n💸 Total Transfers: {total_transfers}"
    send_otp(message)
