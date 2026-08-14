import sqlite3

connection = sqlite3.connect("hospital.db")
cursor = connection.cursor()

cursor.execute("""
DELETE FROM doctors
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM doctors
    GROUP BY doctor, time
)
""")

connection.commit()
connection.close()

print("Duplicate dr slots removed.")