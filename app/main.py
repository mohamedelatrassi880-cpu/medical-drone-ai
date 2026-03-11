from fastapi import FastAPI, UploadFile, File
from google import genai
from pydantic import BaseModel
from PIL import Image
import io
import json

app = FastAPI(title="Medical Drone API")

class PrescriptionData(BaseModel):
    patient_name: str
    medication: str
    dosage: str

client = genai.Client(api_key="AIzaSyBQP9xjoMURYgijXu5qsKqT2WDOHD-bzS0")

# --- 1. THE MOCK DATABASE ---
# This simulates the drone hub's current warehouse inventory
INVENTORY = {
    "Paracetamol": 100,
    "Insulin": 10,
    "Amoxicillin": 0  # Uh oh, we are out of stock!
}

# This simulates the legal registry of valid prescriptions
AUTHORIZED_PATIENTS = {
    "John Doe": ["Paracetamol", "Insulin"],
    "Jane Smith": ["Amoxicillin"]
}

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
        
        # Step B: The Permission & Stock Logic
        status = "Pending"
        reason = ""

        # Check 1: Does the patient have permission for this drug?
        if patient not in AUTHORIZED_PATIENTS or medication not in AUTHORIZED_PATIENTS.get(patient, []):
            status = "DENIED"
            reason = f"Security Alert: {patient} does not have a valid prescription for {medication}."
            
        # Check 2: Do we have it in the warehouse?
        elif INVENTORY.get(medication, 0) <= 0:
            status = "DENIED"
            reason = f"Inventory Alert: {medication} is currently out of stock."
            
        # Check 3: Approved for takeoff!
        else:
            status = "APPROVED"
            reason = f"Success! {medication} is in stock. Dispatching drone to {patient}."
            # (In a real app, we would subtract 1 from the inventory here)
            
        # Return the final verdict to the user's phone
        return {
            "extracted_data": ai_data,
            "delivery_status": status,
            "details": reason
        }
        
    except Exception as e:
        return {"error": str(e)}