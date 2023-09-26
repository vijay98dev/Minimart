from django.conf import settings
from twilio.rest import Client
import random
from dotenv import load_dotenv
import os


class MessageHandler:
    phone_number=None
    otp=None
    def __init__(self,phone_number,otp):
        self.phone_number=phone_number
        self.otp=otp

    def send_otp_on_phone(self):
        load_dotenv()
        client=Client(os.getenv('ACCOUNT_SID'),os.getenv('AUTH_TOKEN'))
        message=client.messages.create(
            body=f"Your MiniMart verification code is:{self.otp}",
            from_="+12292672903",
            to='+91'+self.phone_number
        )
        