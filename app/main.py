import os
import sqlite3
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from google import genai
from google.genai import types # NEW: We need this to handle PDFs
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from thefuzz import fuzz

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

app = FastAPI(title="OrdoSafe AI Gateway")

# --- 1. THE MASTER BLUEPRINT ---
class PrescriptionData(BaseModel):
    patient_name: str
    medication: str
    dosage: str
    doctor_name: str
    inpe_code: str = Field(description="The 9-digit INPE code if present, otherwise 'NOT_FOUND'")
    prescription_date: str = Field(description="The date the prescription was written. Format MUST be YYYY-MM-DD. If no date is found, output 'NOT_FOUND'.")
    clinical_analysis: str = Field(description="Briefly explain if the dosage makes medical sense.")
    is_dosage_safe: bool = Field(description="True if dosage is safe, False if dangerously high.")
    requires_pharmacist_review: bool = Field(description="True if there are signs of missing info or fraud.")

@app.post("/ordosafe-verify/")
async def ordosafe_verify(file: UploadFile = File(...)):
    # Read the raw file bytes
    raw_data = await file.read()
    mime_type = file.content_type
    
    # --- REQUIREMENT 5: UNIVERSAL FILE HANDLER ---
    # We dynamically package the file for Gemini based on what the user uploaded
    if mime_type == "application/pdf":
        document_part = types.Part.from_bytes(data=raw_data, mime_type="application/pdf")
    elif mime_type in ["image/jpeg", "image/png", "image/jpg"]:
        document_part = types.Part.from_bytes(data=raw_data, mime_type=mime_type)
    else:
        return {"status": "ERROR", "reason": f"Unsupported format: {mime_type}. Please upload a PDF, JPG, or PNG."}

    prompt = """
    Read this prescription carefully. 
    1. Extract patient name, medication, dosage, doctor's name, INPE code, and the Date.
    2. Format the date strictly as YYYY-MM-DD.
    3. Analyze if the dosage is medically safe.
    """
    
    try:
        # Pass our dynamic document_part to Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, document_part],
            config={
                "response_mime_type": "application/json",
                "response_schema": PrescriptionData,
            }
        )
        extracted_data = json.loads(response.text)
        
        # --- SECURITY LAYER 1: DATE EXPIRATION (90 DAYS) ---
        date_str = extracted_data["prescription_date"]
        if date_str == "NOT_FOUND":
            return {"status": "REJECTED", "reason": "No date found on prescription. Cannot verify legal validity."}
            
        try:
            presc_date = datetime.strptime(date_str, "%Y-%m-%d")
            days_old = (datetime.now() - presc_date).days
            if days_old > 90:
                return {"status": "EXPIRED", "reason": f"Prescription is {days_old} days old. The legal limit is 90 days."}
            elif days_old < 0:
                return {"status": "FRAUD_ALERT", "reason": "The prescription date is in the future!"}
        except ValueError:
            return {"status": "ERROR", "reason": "AI extracted a date, but it was not in a valid format."}

        # --- SECURITY LAYER 2: CLINICAL PHARMACIST CHECK ---
        if not extracted_data["is_dosage_safe"]:
            return {"status": "TOXIC_DOSAGE_ALERT", "reason": "Dangerous dosage detected.", "pharmacist_notes": extracted_data["clinical_analysis"]}
        if extracted_data["requires_pharmacist_review"]:
            return {"status": "PRESCRIPTION_ANOMALY", "reason": "Suspicious or incomplete prescription.", "pharmacist_notes": extracted_data["clinical_analysis"]}

        # --- SECURITY LAYER 3: INPE REGISTRY VERIFICATION ---
        inpe = extracted_data["inpe_code"]
        doctor_ocr = extracted_data["doctor_name"]
        
        conn = sqlite3.connect('drone_hub.db')
        cursor = conn.cursor()
        
        if inpe == "NOT_FOUND":
            conn.close()
            return {"status": "REJECTED", "reason": "No INPE code detected."}
            
        cursor.execute('SELECT full_name, status FROM practitioners WHERE inpe = ?', (inpe,))
        db_record = cursor.fetchone()
        
        if not db_record:
            conn.close()
            return {"status": "FRAUD_ALERT", "reason": f"INPE {inpe} does not exist in the National Registry."}
            
        db_name, status = db_record
        if status != "ACTIVE":
            conn.close()
            return {"status": "REJECTED", "reason": f"Doctor's license is {status} in the Registry."}
            
        similarity = fuzz.token_set_ratio(doctor_ocr.lower(), db_name.lower())
        conn.close()
        
        if similarity < 75:
            return {"status": "FLAGGED", "reason": f"Name mismatch. OCR read '{doctor_ocr}' but Registry says '{db_name}'."}
            
        # --- FINAL APPROVAL ---
        return {
            "status": "VERIFIED", 
            "reason": "INPE and Doctor Identity confirmed. Clinical dosage safe. Date is legally valid. Ready for Drone Dispatch.",
            "extracted_text": extracted_data
        }

    except Exception as e:
        return {"error": str(e)}