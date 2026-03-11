# Medical Drone AI Core (Group 19)

This is the central intelligence for our **Learning by Doing** project at École Centrale Casablanca. This backend uses **Google Gemini 2.5 Flash** to read handwritten prescriptions and verify them against a local **SQLite** medical database.

---

## System Architecture
1. **The Eyes:** Google Gemini Vision AI (OCR & Entity Extraction).
2. **The Brain:** FastAPI (Python web server handling requests).
3. **The Memory:** SQLite Database (Stores authorized patients and drone hub inventory).



---

## Quick Setup (For Team Members)

Follow these steps to get the AI running on your local machine:

### 1. Environment Setup
Create a virtual environment to keep our libraries separate:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

2. Set Up Your Secrets
You need a Gemini API Key.

Get a free key from Google AI Studio.

Create a file named .env in the root folder.

Paste your key inside: GEMINI_API_KEY=your_key_here
3. Initialize the Warehouse
Run the database builder to create the local drone_hub.db file: python init_db.py
4. Launch the Server
Start the API locally: uvicorn app.main:app --reload

How to Test the AI
Once the server is running:

Open your browser to https://www.google.com/search?q=http://127.0.0.1:8000/docs.

Find the POST /scan-and-verify/ endpoint.

Click "Try it out".

Upload a photo of a prescription (e.g., data/sample.png).

Click "Execute" to see the AI's JSON verdict!

