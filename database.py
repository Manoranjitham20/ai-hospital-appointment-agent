
import sqlite3
import shutil
import os

DB_PATH = "/tmp/hospital.db"
SOURCE_DB = os.path.join(os.path.dirname(__file__), "hospital.db")

def _ensure_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(SOURCE_DB, DB_PATH)

def _normalize(text: str) -> str:
    return text.lower().replace(" ", "")
import sqlite3
def save_appointment(patient, doctor, time):
    patient = _normalize(patient)
    doctor = _normalize(doctor)
    time = _normalize(time)

    _ensure_db()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        patient TEXT,
        doctor TEXT,
        time TEXT
    )
    """)

    cursor.execute(
        "INSERT INTO appointments VALUES(?,?,?)",(
        _normalize(patient), _normalize(doctor), _normalize(time)
    ))

    connection.commit()
    connection.close()

    return f"{patient} appointment booked with {doctor} at {time}"
import sqlite3
def get_patient_appointment(patient,doctor):
    _ensure_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM appointments WHERE patient=? AND doctor=? ",(_normalize(patient), _normalize(doctor)))
    row = cursor.fetchall()
    connection.close()
    if not row:
        return f"No appointment found for {patient} with {doctor}"

    lines = [
        f"Patient: {p}\nDoctor: {d}\nTime: {t}"
        for p, d, t in row
    ]
    return "\n\n".join(lines)
import sqlite3
def cancel_appointment(patient, doctor, time):
    _ensure_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM appointments WHERE patient=? AND doctor=? AND time=?",(
        _normalize(patient), 
        _normalize(doctor), 
        _normalize(time)
    ))
    row = cursor.fetchone()
 
    if not row:
        connection.close()
        return f"No appointment found for {patient} with {doctor} at {time}"

    cursor.execute(
        "DELETE FROM appointments WHERE patient=? AND doctor=? AND time=?",
        (patient, doctor, time)
    )
    connection.commit()
    connection.close()

    _ensure_db()
 
    connection2 = sqlite3.connect(DB_PATH)
    cursor2 = connection2.cursor()
    cursor2.execute(
        "INSERT INTO doctors (doctor, time) VALUES (?, ?)",
        (_normalize(doctor), _normalize(time))
    )
    connection2.commit()
    connection2.close()
 
    return f"{patient}'s appointment with {doctor} at {time} has been cancelled"
import sqlite3
def update_appointment(patient, doctor, old_time, new_time):
    _ensure_db()
   
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT time FROM doctors WHERE doctor=?", (_normalize(doctor),))
    rows = cursor.fetchall()
    connection.close()
 
    slots = [_normalize(r[0]) for r in rows]
    new_time_n = _normalize(new_time)
 
    if new_time_n not in slots:
        return f"Cannot reschedule. {new_time} is not available. Available slots: {', '.join(slots)}"

    _ensure_db()
 
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE appointments SET time=? WHERE patient=? AND doctor=? AND time=?",
        (_normalize(new_time), 
         _normalize(patient), 
         _normalize(doctor), 
         _normalize(old_time))
    )
    updated_rows = cursor.rowcount
    connection.commit()
    connection.close()
 
    if updated_rows == 0:
        return f"No existing appointment found for {patient} with {doctor} at {old_time}"

    _ensure_db()
 
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM doctors WHERE doctor=? AND time=?",
        (_normalize(doctor), new_time_n)
    )
    cursor.execute(
        "INSERT INTO doctors (doctor, time) VALUES (?, ?)",
        (_normalize(doctor), _normalize(old_time))
    )
    connection.commit()
    connection.close()
 
    return f"{patient}'s appointment with {doctor} rescheduled from {old_time} to {new_time}"
import sqlite3
def get_slots(doctor):
    _ensure_db()
    connection = sqlite3.connect(DB_PATH)
    cursor=connection.cursor()
    cursor.execute(
        "SELECT time FROM doctors WHERE doctor=?", (_normalize(doctor),)
    )
    rows = cursor.fetchall()
    connection.close()
    slots=[]
    for row in rows:
        slots.append(row[0])
        
    return slots
import sqlite3

def get_doctor_details():
    _ensure_db()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT doctor FROM doctors"
    )
    rows=cursor.fetchall()
    connection.close()
    doctor=[]
    for row in rows:
        doctor.append(row[0])
    return doctor

def appointment_exists(patient, doctor, time):
    _ensure_db()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT 1 FROM appointments WHERE patient=? AND doctor=? AND time=?",
        (
            _normalize(patient),
            _normalize(doctor),
            _normalize(time)
        )
    )

    existing = cursor.fetchone()

    connection.close()

    return existing is not None


