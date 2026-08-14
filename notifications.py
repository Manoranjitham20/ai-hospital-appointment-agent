from twilio.rest import Client
import smtplib
from email.message import EmailMessage

import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_whatsapp(phone, patient, doctor, time):
  
    t_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = t_client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
        to=f"whatsapp:{phone}",
        body=f"""
Hello {patient},

Your appointment has been confirmed.

Doctor: {doctor}
Time: {time}
"""
    )

    return message.sid
def send_email(to_email, patient, doctor, time):


    msg = EmailMessage()
    msg["Subject"] = "Appointment Confirmation"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    msg.set_content(
        f"""
Hello {patient},

Your appointment has been confirmed.

Doctor : {doctor}
Time : {time}

Thank you.
"""
    )
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return "Email sent successfully."
    except Exception as e:
        print(e)
