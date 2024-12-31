from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
import pytesseract
import cv2
import numpy as np
from database import get_db
from models import MedicalRecord
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Set the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path as necessary

# OCR function
def process_image_for_ocr(image_data: bytes) -> str:
    np_arr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Uploaded file is not a valid image.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    extracted_text = pytesseract.image_to_string(thresh)
    return extracted_text

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Data Extraction API"}

# Endpoint for uploading files
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        logger.error("File format not supported.")
        raise HTTPException(status_code=400, detail="File format not supported. Please upload a JPEG or PNG image.")

    try:
        contents = await file.read()
        extracted_text = process_image_for_ocr(contents)

        # Insert the extracted data into the database
        patient_name = "John Doe"  # Replace with actual logic to get patient name if needed
        new_record = MedicalRecord(patient_name=patient_name, extracted_text=extracted_text)
        db.add(new_record)
        db.commit()

        return {"message": "File processed and data saved.", "extracted_text": extracted_text}
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint for retrieving extracted data
@app.get("/data/")
def get_extracted_data(db: Session = Depends(get_db)):
    records = db.query(MedicalRecord).all()
    result = [
        {
            "Patient Name": record.patient_name,
            "Extracted Text": record.extracted_text
        }
        for record in records
    ]
    return result
