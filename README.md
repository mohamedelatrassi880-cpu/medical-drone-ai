# 🚁 OrdoSafe AI Gateway - Medical Drone Backend

A secure, AI-powered FastAPI backend designed to verify medical prescriptions before authorizing drone delivery. This system acts as a digital pharmacist and identity gateway, ensuring that all deliveries are legally compliant, medically safe, and authorized by a registered practitioner.

---

## ✨ Core Features
1. **AI Handwriting Recognition (OCR):** Uses Google Gemini 2.5 Flash to extract patient data, medications, and dosages from messy, handwritten prescriptions.
2. **INPE Detection & Verification:** Extracts the 9-digit INPE code and cross-references it against a local SQLite database using fuzzy-matching to forgive OCR typos.
3. **AI Pharmacist Coherence Check:** Automatically flags lethal overdoses, illogical prescriptions, and enforces the Moroccan 90-day prescription expiration law.
4. **Universal Digital Support:** Seamlessly processes both image files (JPG, PNG) and digital e-prescriptions (PDFs).

---

## 🚀 Installation & Setup

**1. Create and activate a virtual environment:**
```bash
python -m venv .venv
.\.venv\Scripts\activate 
```
**2. Install dependencies:**
```bash
pip install fastapi uvicorn google-genai pydantic pillow python-dotenv thefuzz rapidfuzz python-multipart
```
**3. Configure Environment Variables:**
Create a file named .env in the root directory and paste your API key:
```Code snippet
GEMINI_API_KEY=your_api_key_here
```
**4. Initialize the Database:**
Run the database builder to create the local drone_hub.db file and populate it with our mock ANAM registry:
```bash
python init_db.py
```
## How to Test the AI
**1. Start the Server:**
```bash
uvicorn app.main:app --reload
```
**2. Test the Endpoint:**
Open your browser and go to: http://127.0.0.1:8000/docs

Find the POST /ordosafe-verify/ endpoint.

Click "Try it out".

Upload a photo of a prescription or a PDF.

Click "Execute" to see the AI's JSON verification report!