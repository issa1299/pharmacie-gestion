import base64
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class SmsNotConfigured(Exception):
    pass


def send_sms(to_number, message):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
    from_number = os.environ.get('TWILIO_FROM_NUMBER', '')

    if not account_sid or not auth_token or not from_number:
        raise SmsNotConfigured("Twilio n'est pas configure.")

    data = urlencode({
        'To': to_number,
        'From': from_number,
        'Body': message,
    }).encode()
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    request = Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        data=data,
        headers={
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        method='POST',
    )

    with urlopen(request, timeout=15) as response:
        return response.read().decode()
