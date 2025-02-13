import boto3
from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import os

app = FastAPI()

# AWS Credentials (Replace with your actual keys)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
# Default to us-east-1 if not set
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize Rekognition Client
rekognition_client = boto3.client(
    "rekognition",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


def read_image(image_data):
    """Convert image bytes to OpenCV format"""
    image_array = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


@app.get("/")
def home():
    return {"message": "Face Matching API using AWS Rekognition is Running!"}


@app.post("/match_faces/")
async def match_faces(license_image: UploadFile = File(...), selfie_image: UploadFile = File(...)):
    try:
        # Read images as bytes
        license_face_bytes = await license_image.read()
        selfie_bytes = await selfie_image.read()

        # Call AWS Rekognition CompareFaces API
        response = rekognition_client.compare_faces(
            SourceImage={"Bytes": license_face_bytes},
            TargetImage={"Bytes": selfie_bytes},
            SimilarityThreshold=85,  # Adjust similarity threshold as needed
        )

        # Check if faces match
        if response["FaceMatches"]:
            confidence = response["FaceMatches"][0]["Similarity"]
            return {"match": True, "confidence": confidence}
        else:
            return {"match": False, "confidence": 0}

    except Exception as e:
        return {"error": str(e)}
