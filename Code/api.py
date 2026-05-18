from fastapi import FastAPI, UploadFile, File
import os
import shutil

# Import the core engine
from underwriter import process_underwriting

# Initialize the API
app = FastAPI(
    title="Atidan AI Underwriter API",
    description="Automated Credit Scoring and GST Verification API"
)

# Create the endpoint
@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Accepts a financial PDF, runs the RAG extraction, performs GST verification, 
    and returns a Credit Risk JSON.
    """
    # 1. Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Hand the file to core engine
        print(f"Processing new file via API: {file.filename}")
        result = process_underwriting(temp_file_path)
        
        # 3. Return the exact JSON dictionary engine creates
        return result
        
    finally:
        # 4. Clean up the server (delete the temp file)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "API is live and waiting for PDFs."}