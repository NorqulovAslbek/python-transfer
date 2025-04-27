import functools
import logging
import time

from jsonrpcserver import Error


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'ip'):
            record.ip = 'unknown'
        if not hasattr(record, 'ext_id'):
            record.ext_id = 'N/A'
        return super().format(record)


logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger('custom')


def log_request_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        context = args[0] if args else None

        ip_address = 'unknown'
        if context:
            ip_address = context.META.get('REMOTE_ADDR', 'unknown')
            if not ip_address or ip_address == 'unknown':
                ip_address = context.META.get('HTTP_X_FORWARDED_FOR', 'unknown')
                if ip_address:
                    ip_address = ip_address.split(',')[0].strip()

        params = {}
        if len(args) > 1:
            params = args[1]
            if len(args) > 2:
                params = {
                    'card_number': args[1],
                    'expire': args[2]
                }

        ext_id = params.get('ext_id', 'N/A') if isinstance(params, dict) else 'N/A'

        try:
            response = func(*args, **kwargs)
            processing_time = time.time() - start_time
            sender_card_number = kwargs.get('sender_card_number', '')
            receiver_card_number = kwargs.get('receiver_card_number', '')
            request = {}
            if sender_card_number and receiver_card_number:
                request = {
                    "ext_id": kwargs.get('ext_id'),
                    "sender_card_number": sender_card_number[:4] + '****' + sender_card_number[-4:],
                    "sender_card_expiry": kwargs.get("sender_card_expiry"),
                    "sender_phone": kwargs.get("sender_phone"),
                    "receiver_card_number": receiver_card_number[:4] + '****' + receiver_card_number[-4:],
                    "receiver_phone": kwargs.get("receiver_phone"),
                    "sending_amount": kwargs.get("sending_amount"),
                    "currency": kwargs.get("currency")
                }
            elif kwargs['ext_id'] and kwargs['otp']:
                request = {
                    "ext_id": kwargs.get('ext_id'),
                    "otp": "******"
                }
            elif kwargs['ext_id']:
                request = {
                    "ext_id": kwargs.get('ext_id')
                }

            if hasattr(response, 'message') and hasattr(response, 'code'):
                response_str = f"Xato: {response.message} (code: {response.code})"
            else:
                response_str = str(response)
            logger.info(
                f"Method: {func.__name__}, Request: {request}, "
                f"Response: {response_str}, Time: {processing_time:.3f}s",
                extra={'ip': ip_address, 'ext_id': ext_id}
            )
            return response
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Method: {func.__name__}, Error: {str(e)}, Time: {processing_time:.3f}s",
                extra={'ip': ip_address, 'ext_id': ext_id}
            )
            return Error(code=500, message=f"{str(e)}")

    return wrapper
