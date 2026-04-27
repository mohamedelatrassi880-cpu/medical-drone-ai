import sqlite3

conn = sqlite3.connect('drone_hub.db')
cursor = conn.cursor()

print("🔨 Building the database tables...")

# 1. Create the Inventory Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        medication TEXT PRIMARY KEY,
        quantity INTEGER
    )
''')

# 2. Create the Authorized Patients Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS authorized_patients (
        patient_name TEXT,
        allowed_medication TEXT
    )
''')

# 3. Create the INPE Registry Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS practitioners (
        inpe TEXT PRIMARY KEY,
        full_name TEXT,
        specialty TEXT,
        status TEXT
    )
''')

print("📦 Stocking the warehouse and registry...")

# Clear old data just in case
cursor.execute('DELETE FROM inventory')
cursor.execute('DELETE FROM authorized_patients')
cursor.execute('DELETE FROM practitioners')

# Insert Inventory
cursor.executemany('''
    INSERT INTO inventory (medication, quantity) VALUES (?, ?)
''', [
    ("Paracetamol", 100),
    ("Insulin", 10),
    ("Amoxicillin", 0)
])

# Insert Patients
cursor.executemany('''
    INSERT INTO authorized_patients (patient_name, allowed_medication) VALUES (?, ?)
''', [
    ("John Doe", "Paracetamol"),
    ("John Doe", "Insulin"),
    ("Jane Smith", "Amoxicillin")
])

# Insert Doctors
mock_doctors = [
    ("123456789", "Dr. Youssef Amrani", "General Practice", "ACTIVE"),
    ("987654321", "Dr. Sara Bennani", "Cardiology", "SUSPENDED"),
    
    # --- YOUR CUSTOM PROTOTYPE DOCTORS ---
    ("111222333", "Dr. Rym Nassih", "Pediatric Oncology", "ACTIVE"),
    ("444555666", "Dr. Primo", "Chief Medical Officer", "ACTIVE"),
    ("777888999", "Dr. Hassan", "Neurology", "ACTIVE")
]
cursor.executemany('INSERT INTO practitioners VALUES (?, ?, ?, ?)', mock_doctors)

# Save everything and close the door
conn.commit()
conn.close()

print("✅ OrdoSafe Database Upgrade Complete!")