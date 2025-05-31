import os
import sqlite3
import face_recognition
from PIL import Image
import imageio
import numpy as np
import time

DB_PATH = "voting_system.db"
IMAGE_DIR = "static/voter_images"

def create_connection():
    return sqlite3.connect(DB_PATH)

def capture_image(voter_id):
    print("[INFO] Capturing image. Look at the camera...")

    try:
        reader = imageio.get_reader("<video1>")  # Try default camera
    except Exception:
        try:
            reader = imageio.get_reader("<video0>")  # Try backup device
        except Exception:
            raise RuntimeError("❌ Unable to access any webcam device.")

    for i, frame in enumerate(reader):
        if i == 20:  # wait for the camera to warm up
            image_path = os.path.join(IMAGE_DIR, f"{voter_id}.jpg")
            imageio.imwrite(image_path, frame)
            reader.close()
            print(f"[INFO] Image saved to {image_path}")
            return image_path
        time.sleep(0.1)

def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        return encodings[0].tobytes()
    else:
        raise ValueError("❌ No face detected in the image!")

def register_voter(voter_id, name):
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    image_path = capture_image(voter_id)
    encoding = encode_face(image_path)

    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO voters (voter_id, name, image_path, encoding, has_voted) VALUES (?, ?, ?, ?, ?)",
                       (voter_id, name, image_path, encoding, 0))
        conn.commit()
        print("✅ Voter registered successfully.")
    except sqlite3.IntegrityError:
        print("⚠️ Voter ID already registered.")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== VOTER REGISTRATION ===")
    voter_id = input("Enter Voter ID: ")
    name = input("Enter Full Name: ")
    register_voter(voter_id, name)
