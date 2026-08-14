from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]
def _normalize(text: str) -> str:
    return text.lower().replace(" ", "")

def get_calendar_service():

    token_json = os.getenv("GOOGLE_TOKEN_JSON")

    if not token_json:
        raise Exception("GOOGLE_TOKEN_JSON is not configured")

    token_data = json.loads(token_json)

    creds = Credentials.from_authorized_user_info(
        token_data,
        SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service

from datetime import datetime, timedelta

def add_calendar_event(patient, doctor, date, time):

    service = get_calendar_service()

    start = datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %I%p"
    )

    end = start + timedelta(minutes=30)

    event = {
        "summary": f"Appointment - {patient}",
        "description": f"Doctor: {doctor}",
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }

    event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return event["htmlLink"]
if __name__ == "__main__":
    link = add_calendar_event(
        "Mano",
        "Dr.Siva",
        "2026-08-03",
        "08PM"
    )

    print(link)