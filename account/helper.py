from django.conf import settings
from twilio.rest import Client
import random



class MessageHandler:
    phone_number=None
    otp=None
    def __init__(self,phone_number,otp):
        self.phone_number=phone_number
        self.otp=otp

    def send_otp_on_phone(self):
        client=Client(settings.ACCOUNT_SID,settings.AUTH_TOKEN)
        message=client.messages.create(
            body=f"Your MiniMart verification code is:{self.otp}",
            from_="+12292672903",
            to='+91'+self.phone_number
        )
        print(message.sid)
        