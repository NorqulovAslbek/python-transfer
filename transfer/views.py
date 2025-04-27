from datetime import timezone, datetime

import bcrypt
from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import Error, Success, dispatch, method
from jsonrpcserver.result import Result

from excell.models import Card
from logger.logger import log_request_response
from transfer.check_card.check import is_card_expired
from transfer.check_card.convert_balance import valyuta, convert_rub_to_uzs
from transfer.check_card.create_otp import otp_code
from transfer.check_card.send_otp_telegram import send_otp_telegram
from transfer.models import Transfer, TransferState


@method(name='card.info')
@log_request_response
def card_info(context, card_number, expire):
    """
    ------------------------------------------------------------------------------------
    Retrieves information about a specific card using card number and expiry date.
    Results are cached for 30 seconds to improve performance.
    ------------------------------------------------------------------------------------
    :param context: The request context or session object.
    :param card_number: The number of the card to retrieve information for.
                        card_number -> this is the type of variable str
    :param expire: The expiry date of the card (e.g., '12/25').
                   expire -> this is the type of variable str
    :return: A dictionary containing card details if found, otherwise an error message.
             Example: {"card_number", "expire", "balance", ...}
    """
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
    """
    ------------------------------------------------------------------------------------------------------------
    Initiates a money transfer between two cards after validating card details,
    ensuring sufficient balance, and sending an OTP for verification.
    ------------------------------------------------------------------------------------------------------------
     Parameters:
    :param context: The request context or session object.
    :param ext_id: A unique external identifier for the transfer request. ext_id -> this is the type of variable str
    :param sender_card_number : The card number of the sender. sender_card_number -> this is the type of variable str
    :param sender_card_expiry : Expiry date of the sender's card (e.g. '12/25'). this is the type of variable str
    :param  sender_phone : Phone number associated with the sender's card.  this is the type of variable str
    :param receiver_card_number : The card number of the receiver. this is the type of variable str
    :param receiver_phone : Phone number associated with the receiver's card. this is the type of variable str
    :param sending_amount : The amount of money to be transferred. this is the type of variable float
    :param currency : The currency of the sending amount (e.g. 'RUB', 'UZS'). this is the type of variable str
    :return: {"ext_id","state"}
    """
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
def confirm_transfer(context, ext_id, otp) -> Result:
    """
    ------------------------------------------------------------------------------------
    Confirms a pending transfer using a provided OTP code. Validates the transfer state,
    checks the OTP, updates card balances, and marks the transfer as confirmed.
    ------------------------------------------------------------------------------------
    :param context: The request context or session object.
    :param ext_id: A unique external identifier for the transfer request. ext_id -> this is the type of variable str
    :param otp:  The one-time password sent to the sender for verification. this is the type of variable  str
    :return: {"ext_id","state"}
    """
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return Error(message="not found transfer!", code=404)

    if transfer.try_count >= 3:
        return Error(message="Attempt limit exceeded.", code=429)

    if not bcrypt.checkpw(otp.encode(), transfer.otp.encode()):
        transfer.try_count += 1
        transfer.save()
        return Error(message="Invalid code!", code=400)

    if transfer.state != TransferState.CREATED:
        return Error(message="Transfer is in an invalid state!", code=400)
    else:
        sender_card = Card.objects.get(card_number=transfer.sender_card_number)
        receiver_card = Card.objects.get(card_number=transfer.receiver_card_number)
        sender_card.balance -= transfer.sending_amount
        sender_card.save(update_fields=['balance'])
        receiver_card.balance += transfer.receiving_amount
        receiver_card.save(update_fields=['balance'])
        transfer.state = TransferState.CONFIRMED
        transfer.confirmed_at = timezone.now()
        transfer.save(update_fields=['state', 'confirmed_at'])
        return Success(transfer.to_result())


@method(name="transfer_cancel")
@log_request_response
def transfer_cancel(context, ext_id) -> Result:
    """
    ------------------------------------------------------------------------------------
    Cancels a previously confirmed transfer by reverting the transaction between
    sender and receiver cards, and marking the transfer as cancelled.
    ------------------------------------------------------------------------------------
    :param context: The request context or session object.
    :param ext_id: A unique external identifier for the transfer request.ext_id -> this is the type of variable str
    :return: {"ext_id", "state"}
    """
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

    if transfer.sending_amount >= convert_rub_to_uzs(receiver_card.balance):
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
def transfer_state(context, ext_id):
    """
    ------------------------------------------------------------------------------------
    Returns the current state/status of a transfer based on the provided external ID.
    ------------------------------------------------------------------------------------
    :param context: The request context or session object.
    :param ext_id: A unique external identifier for the transfer request.
                   ext_id -> this is the type of variable str
    :return: {"message"} where message contains the current state of the transfer
    """
    try:
        transfer = Transfer.objects.get(ext_id=ext_id)
        return Success({"message": transfer.state})
    except Transfer.DoesNotExist:
        return Error(message="transfer not found!", code=404)


@method(name="transfer_filter")
def transfer_filter(context, card_number, start_date=None, end_date=None, status=None):
    """
    ------------------------------------------------------------------------------------
    Filters transfer history based on the sender card number, optional date range,
    and status. Returns a list of matching transfers with basic info.
    ------------------------------------------------------------------------------------
    :param context: The request context or session object.
    :param card_number: Sender’s card number to filter transfers.
                        card_number -> this is the type of variable str
    :param start_date: (Optional) Start date to filter transfers from (format: YYYY-MM-DD).
                       start_date -> this is the type of variable str
    :param end_date: (Optional) End date to filter transfers to (format: YYYY-MM-DD).
                     end_date -> this is the type of variable str
    :param status: (Optional) Status of the transfer (e.g., 'created', 'confirmed', 'cancelled').
                   status -> this is the type of variable str
    :return: A list of dictionaries containing:
             {"ext_id", "amount", "currency", "receiver", "state", "created_at"}
    """
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
