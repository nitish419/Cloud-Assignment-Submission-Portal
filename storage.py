import os
import shutil
from fastapi import UploadFile
from datetime import datetime

# Simulating an S3 Bucket locally
STORAGE_BUCKET = "../uploads"

os.makedirs(STORAGE_BUCKET, exist_ok=True)

def upload_to_cloud(file: UploadFile, assignment_id: int, student_id: int) -> str:
    """
    Simulates uploading a file to Cloud Object Storage.
    Returns the storage URI.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{student_id}_{timestamp}_{file.filename}"
    
    # Simulate S3 Key path: /assignments/1/student_5/file.pdf
    storage_path = os.path.join(STORAGE_BUCKET, f"assign_{assignment_id}")
    os.makedirs(storage_path, exist_ok=True)
    
    file_location = os.path.join(storage_path, safe_filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # Return simulated cloud URL
    return file_location