import cv2
import os
import pytesseract
from PIL import Image
import re

CAPTURE_FOLDER = "static/captured_images/"

# Open Camera and Start Video Feed
class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return None
        _, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()

    def capture_image(self, filename="captured_image.jpg"):
        ret, frame = self.video.read()
        if not ret:
            raise Exception("Failed to capture image.")

        if not os.path.exists(CAPTURE_FOLDER):
            os.makedirs(CAPTURE_FOLDER)

        image_path = os.path.join(CAPTURE_FOLDER, filename)
        cv2.imwrite(image_path, frame)
        self.__del__()
        return image_path
    
    


# Extract Data from Aadhaar Card
def extract_aadhaar_data(text):
    name, dob, uid = None, None, None

    # Extract UID (12 digits for Aadhaar)
    uid_match = re.search(r"\b\d{12}\b", text)
    if uid_match:
        uid = uid_match.group()

    # Extract Date of Birth
    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if dob_match:
        dob = dob_match.group()

    # Extract Name (Basic Pattern Match for Name Line)
    lines = text.split("\n")
    if len(lines) > 2:
        name = lines[1]

    return {"Name": name, "DOB": dob, "UID": uid}


# Extract Data from PAN Card
def extract_pan_data(text):
    name, fname, dob, pan = None, None, None, None

    # Extract PAN Number Pattern (ABCDE1234F)
    pan_match = re.search(r"[A-Z]{5}\d{4}[A-Z]{1}", text)
    if pan_match:
        pan = pan_match.group()

    # Extract Date of Birth
    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    if dob_match:
        dob = dob_match.group()

    lines = text.split("\n")
    if len(lines) >= 3:
        name = lines[0]
        fname = lines[1]

    return {"Name": name, "Father Name": fname, "DOB": dob, "PAN": pan}
