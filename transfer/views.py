import random
from datetime import timezone

from jsonrpcserver import Error, Success, dispatch, method
from jsonrpcserver.result import ErrorResult, SuccessResult, Result

from excell.models import Card
from transfer.check_card.check import is_card_expired
from transfer.check_card.convert_balance import valyuta
from transfer.check_card.send_otp_telegram import send_otp_telegram
from transfer.models import Transfer
from django.utils import timezone

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@method(name="transfer_create")
def transfer_create(
        ext_id,
        sender_card_number,
        sender_card_expiry,
        sender_phone,
        receiver_card_number,
        receiver_phone,
        sending_amount,
        currency
) -> Result:
    if Transfer.objects.filter(ext_id=ext_id).first():
        return Error("ext_id exists")
    try:
        sender_card = Card.objects.get(card_number=sender_card_number)
        if sender_card.phone == "None" or sender_card.balance < sending_amount or sender_card.status != 'active' or is_card_expired(
                sender_card_expiry):
            return Error("Yuboruvchi karta yaroqsiz , mablag' yetarli emas!")
    except Card.DoesNotExist:
        return Error("card not found!")
    try:
        receiver_card = Card.objects.get(card_number=receiver_card_number)
        if receiver_card.status != "active" or is_card_expired(receiver_card.expire):
            return Error("qabul qiluvchi yaroqsiz!")
    except Card.DoesNotExist:
        return Error("receiver card not found!")
    val = valyuta(sending_amount, currency)
    convert_amount = val['converted_amount']
    otp = random.randint(100000, 999999)
    chat_id = 6656413541
    send_otp_telegram(chat_id, otp)
    Transfer.objects.create(
        ext_id=ext_id,
        sender_card_number=sender_card_number,
        sender_card_expiry=sender_card_expiry,
        sender_phone=sender_phone,
        receiver_card_number=receiver_card_number,
        receiver_phone=receiver_phone,
        sending_amount=sending_amount,
        currency=currency,
        receiving_amount=convert_amount,
        state="created",
        try_count=0,
        otp=otp,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    return Success({
        "message": "transfer created",
        "ext_id": ext_id
    })


@method(name="confirm_transfer")
def confirm_transfer(ext_id, otp) -> Result:
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return Error("not found transfer!")
    if transfer.state != 'created':
        return Error("transfer noto'gri state da")
    if transfer.try_count >= 3:
        return Error("urinishlar soni ortib ketti")

    if transfer.otp != otp:
        transfer.try_count += 1
        transfer.save()
        return Error("hato kiritilgan kod!")

    sender_card = Card.objects.get(card_number=transfer.sender_card_number)
    receiver_card = Card.objects.get(card_number=transfer.receiver_card_number)
    sender_card.balance -= transfer.sending_amount
    receiver_card.balance += transfer.receiving_amount
    sender_card.save()
    receiver_card.save()

    transfer.state = 'confirmed'
    transfer.confirmed_at = timezone.now()
    transfer.updated_at = timezone.now()
    transfer.save()
    return Success({"message": "pul muvoqyatli otdi"})


@method(name="transfer_cancel")
def transfer_cancel(ext_id) -> Result:
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return Error("transfer not fount!")
    if transfer.state == "cancelled":
        return Error("transfer allaqachon qaytarilgan!")

    sender_card = Card.objects.get(card_number=transfer.sender_card_number)
    receiver_card = Card.objects.get(card_number=transfer.receiver_card_number)
    sender_card.balance += transfer.sending_amount
    receiver_card.balance -= transfer.receiving_amount
    sender_card.save()
    receiver_card.save()
    transfer.state = "cancelled"
    transfer.updated_at = timezone.now()
    transfer.cancelled_at = timezone.now()
    transfer.save()
    return Success({"message": "transfer mufoqyatli qaytarildi!"})


@csrf_exempt
def jsonrpc(request):
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
