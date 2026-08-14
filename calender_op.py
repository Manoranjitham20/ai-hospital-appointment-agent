from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)

    return service
if __name__ == "__main__":
    service = get_calendar_service()
    print("Google Calendar Connected Successfully")

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