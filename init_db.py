import sqlite3

conn = sqlite3.connect('drone_hub.db')
cursor = conn.cursor()

print("🔨 Building the database tables...")

# Create the Inventory Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        medication TEXT PRIMARY KEY,
        quantity INTEGER
    )
''')

# Create the Authorized Patients Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS authorized_patients (
        patient_name TEXT,
        allowed_medication TEXT
    )
''')

print("📦 Stocking the warehouse with initial supplies...")

# Clear old data just in case
cursor.execute('DELETE FROM inventory')
cursor.execute('DELETE FROM authorized_patients')

# Insert our starting data
cursor.executemany('''
    INSERT INTO inventory (medication, quantity) VALUES (?, ?)
''', [
    ("Paracetamol", 100),
    ("Insulin", 10),
    ("Amoxicillin", 0)
])

cursor.executemany('''
    INSERT INTO authorized_patients (patient_name, allowed_medication) VALUES (?, ?)
''', [
    ("John Doe", "Paracetamol"),
    ("John Doe", "Insulin"),
    ("Jane Smith", "Amoxicillin")
])

conn.commit()
conn.close()

print("✅ Database successfully created and populated!")