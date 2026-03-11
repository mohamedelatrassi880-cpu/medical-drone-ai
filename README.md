#  Medical Drone AI Core
This is the AI-powered backend for Group 19's Medical Delivery Drone project.

##  Setup Instructions
1. **Environment:** Run `python -m venv .venv` and activate it.
2. **Install:** Run `pip install -r requirements.txt`
3. **Database:** Run `python init_db.py` to create your local warehouse.
4. **API Key:** Create a `.env` file and add your `GEMINI_API_KEY`.
5. **Run:** Start the server with `uvicorn app.main:app --reload`