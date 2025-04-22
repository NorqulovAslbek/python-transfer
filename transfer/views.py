from datetime import timezone, datetime

import bcrypt
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import Error, Success, dispatch, method
from jsonrpcserver.result import Result

from excell.models import Card
from transfer.check_card.check import is_card_expired
from transfer.check_card.convert_balance import valyuta
from transfer.check_card.send_otp_telegram import send_otp_telegram
from transfer.models import Transfer, TransferState
from transfer.check_card.create_otp import otp_code
from logger.logger import log_request_response
from django.core.cache import cache


@method(name='card.info')
def card_info(context, card_number, expire):
    card_cache_key = f"cache_key_{card_number}_{expire}"
    card_cache = cache.get(card_cache_key)

    if card_cache:
        return Success(card_cache)

    try:
        card = Card.objects.get(card_number=card_number, expire=expire)
        cache.set(key=card_cache_key, value=card.card_result(), timeout=30)
        return Success(card.card_result())
    except Card.DoesNotExist:
        return Error(message="card not found", code=404)


@method(name="transfer_create")
@log_request_response
def transfer_create(context,
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
        return Error(message="ext_id exists!", code=409)
    try:
        sender_card = Card.objects.get(card_number=sender_card_number)
        if is_card_expired(sender_card_expiry):
            return Error(message="sender card expired!", code=400)
        if sender_card.status != 'active':
            return Error(message="sender card status is inactive", code=400)
        if sender_card.phone == "None":
            return Error(message="sms not connected!", code=400)
        if sender_card.phone != sender_phone:
            return Error(message="both phone numbers are not uniform!", code=400)
        if sender_card.balance < sending_amount:
            return Error(message="your balance is not enough!", code=400)
    except Card.DoesNotExist:
        return Error(message="card not found!", code=404)
    try:
        receiver_card = Card.objects.get(card_number=receiver_card_number)
        if receiver_card.status != "active":
            return Error(message="the receiving card is invalid!", code=400)
        if is_card_expired(receiver_card.expire):
            return Error(message="receiving card expired!", code=400)
        if receiver_card.phone == "None":
            return Error(message="SMS not connected!", code=400)
    except Card.DoesNotExist:
        return Error(message="receiver card not found!", code=404)
    # convert sender amount
    convert_amount = valyuta(sending_amount, currency)
    # otp code generated
    otp = otp_code()
    # send otp cod
    send_otp_telegram(otp)
    code = bcrypt.hashpw(str(otp).encode(), bcrypt.gensalt()).decode()
    transfer = Transfer.objects.create(
        ext_id=ext_id,
        sender_card_number=sender_card_number,
        sender_card_expiry=sender_card_expiry,
        sender_phone=sender_phone,
        receiver_card_number=receiver_card_number,
        receiver_phone=receiver_phone,
        sending_amount=sending_amount,
        currency=currency,
        receiving_amount=convert_amount,
        state=TransferState.CREATED,
        try_count=0,
        otp=code
    )
    return Success(transfer.to_result())


@method(name="confirm_transfer")
@log_request_response
def confirm_transfer(ext_id, otp) -> Result:
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return Error(message="not found transfer!", code=404)
    if transfer.state != TransferState.CREATED:
        return Error(message="Transfer is in an invalid state!", code=400)
    if transfer.try_count >= 3:
        return Error(message="Attempt limit exceeded.", code=429)

    if not bcrypt.checkpw(otp.encode(), transfer.otp.encode()):
        transfer.try_count += 1
        transfer.save()
        return Error(message="Invalid code!", code=400)
    sender_card = Card.objects.get(card_number=transfer.sender_card_number)
    receiver_card = Card.objects.get(card_number=transfer.receiver_card_number)
    # if sender_card.balance < transfer.sending_amount:
    #     return Error(message="You do not have enough balance!", code=400)
    sender_card.balance -= transfer.sending_amount
    receiver_card.balance += transfer.receiving_amount
    sender_card.save()
    receiver_card.save()

    transfer.state = TransferState.CONFIRMED
    transfer.confirmed_at = timezone.now()
    transfer.updated_at = timezone.now()
    transfer.save()
    return Success(transfer.to_result())


@method(name="transfer_cancel")
@log_request_response
def transfer_cancel(ext_id) -> Result:
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return Error(message="transfer not found!", code=404)
    if transfer.state == TransferState.CANCELLED:
        return Error(message="The transfer has already been canceled!", code=123)
    if transfer.state == TransferState.CREATED:
        return Error(message="The transfer has already been created!", code=400)

    sender_card = Card.objects.get(card_number=transfer.sender_card_number)
    receiver_card = Card.objects.get(card_number=transfer.receiver_card_number)

    if transfer.sending_amount >= receiver_card.balance:
        return Error(message="Insufficient funds to be refunded!", code=400)

    sender_card.balance += transfer.sending_amount
    receiver_card.balance -= transfer.receiving_amount
    sender_card.save()
    receiver_card.save()
    transfer.state = "cancelled"
    transfer.cancelled_at = timezone.now()
    transfer.save()

    return Success(transfer.to_result())


@method(name="transfer_state")
def transfer_state(ext_id):
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
        return Success({"message": transfer.state})
    except Transfer.DoesNotExist:
        return Error(message="transfer not found!", code=404)


@method(name="transfer_filter")
def transfer_filter(card_number, start_date=None, end_date=None, status=None):
    filter_by_fields = {
        "sender_card_number": card_number
    }
    if start_date:
        filter_by_fields["created_at__gte"] = datetime.strptime(start_date, "%Y-%m-%d")  # __gte bu kalit soz ,
        # SELECT * FROM transfer WHERE created_at >= strat_date

    if end_date:
        filter_by_fields['created_at__lte'] = datetime.strptime(end_date, "%Y-%m-%d")

    if status:
        filter_by_fields['state'] = status

    transfer_history_list = Transfer.objects.filter(**filter_by_fields)
    result = [
        {
            "ext_id": t.ext_id,
            "amount": float(t.sending_amount),
            "currency": t.currency,
            "receiver": t.receiver_card_number,
            "state": t.state,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for t in transfer_history_list
    ]

    return Success(result)


@csrf_exempt
def jsonrpc(request):
    return HttpResponse(
        dispatch(request.body.decode(), context=request), content_type="application/json"
    )
