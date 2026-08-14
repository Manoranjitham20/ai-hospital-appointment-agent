from openai import OpenAI
import json
import sqlite3
from calender_op import add_calendar_event
import database
import notifications
import os 
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def check_calendar(doctor, date, time):
    doctor = doctor.lower().replace(" ", "")
    time = time.lower().replace(" ", "")
    slots = database.get_slots(doctor)

    if not slots:
        return "Doctor not found"
    if time in slots:
        return "Available"
    return f"Doctor not available at {time}. Available slots {','.join(slots)}"

def book_appointment(patient, doctor,date,time,phone,to_email):
   
    status = check_calendar(doctor,date,time)
    if status != "Available":
        return status
    if not phone:
        return "Please provide your phone number."

    if not to_email:
        return "Please provide your email address."

    existing = database.appointment_exists(patient, doctor, time)

    if existing:
        return f"{patient} already has an appointment with {doctor} at {time}"
    database.save_appointment(patient, doctor, time)
    try:
        add_calendar_event(patient, doctor, date, time)
        calendar_status = "Calendar event created"
    except Exception as e:
        calendar_status = f"Calendar event failed: {e}"
    whatsapp_status = ""
    email_status = ""
    try:
        notifications.send_whatsapp(phone, patient, doctor, time)
        whatsapp_status = "WhatsApp sent to twilio sandbox"
    except Exception as e:
        whatsapp_status = f"WhatsApp failed: {e}"
    
    try:
        notifications.send_email(to_email, patient, doctor, time)
        email_status = "Email sent"
    except Exception as e:
        email_status = f"Email failed: {e}"
    return (
        f"{patient} appointment booked with {doctor} at {time} on {date}\n"
        f"{whatsapp_status}\n"
        f"{email_status}\n"
        f"{calendar_status}\n")

    

    
    
def _normalize(text: str) -> str:
    return text.lower().replace(" ", "")

tools_dict={
    "check_calendar": check_calendar,
    "book_appointment" : book_appointment,
    "cancel_appointment": database.cancel_appointment,
    "update_appointment":database.update_appointment,
    "get_patient_appointment":database.get_patient_appointment,
    "get_slots":database.get_slots,
    "get_doctor_details":database.get_doctor_details
}
tools=[
    {
        "type": "function",
        "function":{
            "name":"book_appointment",
            "description": "book a hospital appointment",
            "parameters":{
                "type":"object",
                "properties":{
                    "patient":{
                        "type":"string",
                        "description":"patient name"
                    },
                    "doctor":{
                        "type":"string",
                        "description":"doctor name"
                    },
                    "time":{
                        "type":"string",
                        "description":"appointment time"
                    },
                    "phone":{
                        "type":"string",
                        "description":"get a phone number from user. tell the user to enter with country code"
                    },
                    "to_email":{
                        "type":"string",
                        "description":"get an email from user"
                    },
                    "date":{
                        "type":"string",
                        "description":"get a appointment date "
                    }
                },
                "required": ["patient","doctor","date","time","phone","to_email"]

            }
        }
    },
    {
        "type":"function",
    "function":{
        "name":"check_calendar",
        "description":"check calendar for the appointment ",
        "parameters":{
            "type":"object",
            "properties":{
                "doctor":{
                    "type":"string",
                    "description":"doctor name"
                },
                "date":{
                    "type":"string",
                    "description":"Appointment date in YYYY-MM-DD format"
                },
                "time":{
                    "type":"string",
                    "description":"time check for appointment for example 9am or 12pm"
                }
            },
            "required":["doctor","date","time"]
        }

    }

},
{
    "type":"function",
    "function":{
        "name":"cancel_appointment",
        "description":"cancel this appointment",
        "parameters":{
            "type":"object",
            "properties":{
                "patient":{
                    "type":"string",
                    "description":"patient name"
                    
                },
                "doctor":{
                    "type":"string",
                    "description":"doctor name"
                },
                "time":{
                    "type":"string",
                    "description":"appointment time"
                }               

            },
            "required":["patient","doctor","time"]
        }
    }
},
{
    "type":"function",
    "function":{
        "name":"update_appointment",
        "description":"update the appointment",
        "parameters":{
            "type":"object",
            "properties":{
                "patient":{
                    "type":"string",
                    "description":"patient name"
                    
                },
                "doctor":{
                    "type":"string",
                    "description":"doctor name"
                },
                "old_time":{
                    "type":"string",
                    "description":"old time"
                },
                "new_time":{
                    "type":"string",
                    "description":"new time"
                }             

            },
            "required":["patient","doctor","old_time","new_time"]
        }
    }
},
{
        "type": "function",
        "function":{
            "name":"get_patient_appointment",
            "description": "get appointment of patient with specific doctor",
            "parameters":{
                "type":"object",
                "properties":{
                    "patient":{
                        "type":"string",
                        "description":"patient name"
                    },
                    "doctor":{
                        "type":"string",
                        "description":"doctor name"
                    },
                    
    
                },
                "required": ["patient","doctor"]

            }
        }
    },
    {
            "type":"function",
        "function":{
            "name":"get_slots",
            "description":" get time slots for a specific dr",
            "parameters":{
                "type":"object",
                "properties":{
                    "doctor":{
                        "type":"string",
                        "description":"doctor name"
                    }
                   
                },
                "required":["doctor"]
            }
    
        }
    
    },
    {
        "type":"function",
        "function":{
            "name":"get_doctor_details",
            "description":"get doctor dtais and show",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
            
        }
    }
]
messages = [
    {
        "role": "system",
        "content": """
You are a hospital appointment assistant vedi. 
For a booking request:
- If patient name is missing, ask for the patient name.
- If doctor name is missing, ask for the doctor name.
- If date is missing, ask for the appointment date.0
Do not ask again for information that the user has aj.j.formation is available.
"""
    }
]
def run_agent(question):
    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools,
        temperature=0
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)

        final_result = []

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            try:
                result = tools_dict[tool_name](**arguments)
            except Exception as e:
                result = f"error: {e}"

            final_result.append(str(result))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        return "\n".join(final_result)

    else:
        messages.append({
            "role": "assistant",
            "content": message.content
        })

        return message.content
    print("Enter Bye or Exit to end the conversation")

