from google import genai
from pydantic import BaseModel
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
# --- 1. DEFINE THE DATABASE BLUEPRINT ---
class PrescriptionData(BaseModel):
    patient_name: str
    medication: str
    dosage: str

# --- 2. THE IGNITION KEY ---
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

image_path = "data/sample.png"

if os.path.exists(image_path):
    print("🚀 Image found! Extracting pure JSON data...")
    img = Image.open(image_path)
    
    try:
        prompt = "Read this prescription. Extract the patient name, the medication name, and the dosage."
        
        # --- 3. FORCE STRUCTURED OUTPUT ---
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img],
            config={
                "response_mime_type": "application/json",
                "response_schema": PrescriptionData,
            }
        )
        
        print("\n--- DATABASE-READY JSON ---")
        print(response.text.strip())
        print("---------------------------")
        
    except Exception as e:
        print(f"Cloud Error: {e}")
else:
    print(f"Error: Could not find image at {image_path}")