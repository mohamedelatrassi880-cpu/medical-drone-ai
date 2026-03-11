import os
import sqlite3
import io
import json
from fastapi import FastAPI, UploadFile, File
from google import genai
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv

# --- 1. SECURE INITIALIZATION ---
load_dotenv() # This secretly loads your .env file!
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

app = FastAPI(title="Medical Drone API")

class PrescriptionData(BaseModel):
    patient_name: str
    medication: str
    dosage: str

# --- 2. THE API ENDPOINT ---
@app.post("/scan-and-verify/")
async def scan_and_verify(file: UploadFile = File(...)):
    print(f"📥 Received file: {file.filename}")
    image_data = await file.read()
    img = Image.open(io.BytesIO(image_data))
    
    prompt = "Read this prescription. Extract the patient name, the medication name, and the dosage."
    
    try:
        # Step A: Extract the JSON using Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img],
            config={
                "response_mime_type": "application/json",
                "response_schema": PrescriptionData,
            }
        )
        ai_data = json.loads(response.text)
        patient = ai_data["patient_name"]
        medication = ai_data["medication"]
        
        # Step B: Connect to the REAL SQLite Database
        conn = sqlite3.connect('drone_hub.db')
        cursor = conn.cursor()
        
        status = "Pending"
        reason = ""

        # Check 1: Is the patient legally authorized for this drug?
        cursor.execute('''
            SELECT * FROM authorized_patients 
            WHERE patient_name = ? AND allowed_medication = ?
        ''', (patient, medication))
        
        if not cursor.fetchone():
            status = "DENIED"
            reason = f"Security Alert: {patient} does not have a valid prescription for {medication}."
            
        else:
            # Check 2: Do we have it in the warehouse?
            cursor.execute('SELECT quantity FROM inventory WHERE medication = ?', (medication,))
            stock_record = cursor.fetchone()
            
            if not stock_record or stock_record[0] <= 0:
                status = "DENIED"
                reason = f"Inventory Alert: {medication} is currently out of stock."
            else:
                status = "APPROVED"
                reason = f"Success! {medication} is in stock. Dispatching drone to {patient}."
                
                # Check 3: Subtract 1 from the warehouse stock!
                new_quantity = stock_record[0] - 1
                cursor.execute('UPDATE inventory SET quantity = ? WHERE medication = ?', (new_quantity, medication))
                conn.commit() # Save the change to the hard drive
                
        # Close the warehouse doors
        conn.close()

        return {
            "extracted_data": ai_data,
            "delivery_status": status,
            "details": reason
        }
        
    except Exception as e:
        return {"error": str(e)}