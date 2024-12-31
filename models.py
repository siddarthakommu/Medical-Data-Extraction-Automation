from sqlalchemy import Column, Integer, String
from database import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    extracted_text = Column(String)
