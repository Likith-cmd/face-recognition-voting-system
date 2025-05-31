from flask import Blueprint, render_template, request, redirect, flash
import sqlite3
import os
import face_recognition
import numpy as np
from werkzeug.utils import secure_filename
from PIL import Image

vote_bp = Blueprint('vote', __name__)

UPLOAD_FOLDER = "static/vote_images"
DB_FILE = "voting_system.db"

@vote_bp.route("/voter_login")
def voter_login():
    return render_template("voter_login.html")

@vote_bp.route("/vote", methods=["POST"])
def vote():
    voter_id = request.form["voter_id"]
    image_file = request.files["image"]

    if not voter_id or not image_file:
        flash("All fields are required.", "danger")
        return redirect("/voter_login")

    filename = secure_filename(image_file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    image_file.save(filepath)

    # Load uploaded image
    unknown_image = face_recognition.load_image_file(filepath)
    unknown_encodings = face_recognition.face_encodings(unknown_image)

    if not unknown_encodings:
        flash("No face detected in the image.", "danger")
        return redirect("/voter_login")

    unknown_encoding = unknown_encodings[0]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT encoding, has_voted FROM voters WHERE voter_id = ?", (voter_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        flash("Voter not found.", "danger")
        return redirect("/voter_login")

    stored_encoding_str, has_voted = result

    if has_voted:
        conn.close()
        flash("You have already voted.", "warning")
        return redirect("/voter_login")

    stored_encoding = np.fromstring(stored_encoding_str[1:-1], sep=' ')

    match = face_recognition.compare_faces([stored_encoding], unknown_encoding)[0]

    if not match:
        conn.close()
        flash("Face does not match our records.", "danger")
        return redirect("/voter_login")

    # Save vote status
    cursor.execute("UPDATE voters SET has_voted = 1 WHERE voter_id = ?", (voter_id,))
    cursor.execute("INSERT INTO votes (voter_id, choice) VALUES (?, ?)", (voter_id, "YourVote"))
    conn.commit()
    conn.close()

    flash("Vote successfully cast.", "success")
    return redirect("/voter_login")
