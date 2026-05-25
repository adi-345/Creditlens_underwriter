from fastapi import FastAPI, UploadFile, File
import os
import shutil
from underwriter import process_underwriting

app = FastAPI(
    title="Atidan AI Underwriter API",
    description="Automated Credit Scoring and GST Verification API"
)

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    temp_file_path = os.path.join("/tmp", f"temp_{file.filename}")
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        return process_underwriting(temp_file_path)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Health check endpoint that accepts both browser loads (GET) and uptime pings (HEAD)
@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "API is live and waiting for PDFs."}