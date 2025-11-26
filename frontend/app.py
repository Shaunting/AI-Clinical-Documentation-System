import os
import uuid
import json
import pymysql
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, flash

# Environment Settings
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXT = {"webm", "wav", "ogg", "mp3", "m4a"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def speech_to_text(audio_path):
    # TODO: replace to real API
    dummy_transcript = f"dummy text"
    return dummy_transcript

def extract_structure_from_transcript(transcript):
    # TODO: extract structure using NLP model/API
    structure = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "transcript_length_chars": len(transcript)
        },
        "participants": ["doctor", "patient"],
        "transcript_preview": transcript[:500],
        "extracted": {
            "chief_complaint": "stomacache",
            "history_of_present_illness": "start 3 days ago after eating spicy food",
            "possible_diagnoses": ["gastritis", "indigestion"],
            "recommended_tests": ["blood test", "abdominal ultrasound"],
            "prescription": [
                {"name": "pillA", "dosage": "twice a day", "notes": "take after meal"}
            ],
            "follow_up": "Re-examination recommended after 1 week"
        },
        "confidence": {
            "overall": 0.75
        }
    }
    return structure

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="clinic",
        cursorclass=pymysql.cursors.DictCursor
    )

# routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/elements")
def elements():
    return render_template("elements.html")

@app.route("/notes")
def notes():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # cursor.execute("SELECT id, p_name, age, diagnosis FROM notes")
        cursor.execute("""
            SELECT v.id, pi.age, pi.sex,
                (SELECT a.date FROM admissions a WHERE a.visit_id = v.id ORDER BY a.date DESC LIMIT 1) AS latest_admission_date,
                (SELECT t.related_condition FROM treatments t WHERE t.visit_id = v.id LIMIT 1) AS primary_diagnosis
            FROM visits v
            LEFT JOIN patient_information pi ON v.id = pi.visit_id
            ORDER BY v.id ASC;
        """)
        notes_list = cursor.fetchall()
        print(notes_list)
    conn.close()
    return render_template("notes.html", notes=notes_list)

@app.route("/note/<int:visit_id>")
def note_detail(visit_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
        cursor.execute("SELECT * FROM visits WHERE id=%s", (visit_id,))
        visit = cursor.fetchone()

        # patient info
        cursor.execute("SELECT * FROM patient_information WHERE visit_id=%s", (visit_id,))
        patient_info = cursor.fetchone()

        # admissions
        cursor.execute("SELECT * FROM admissions WHERE visit_id=%s", (visit_id,))
        admissions = cursor.fetchall()

        # symptoms
        cursor.execute("SELECT * FROM symptoms WHERE visit_id=%s", (visit_id,))
        symptoms = cursor.fetchall()

        # treatments
        cursor.execute("SELECT * FROM treatments WHERE visit_id=%s", (visit_id,))
        treatments = cursor.fetchall()

        # discharge
        cursor.execute("SELECT * FROM discharges WHERE visit_id=%s", (visit_id,))
        discharge = cursor.fetchone()
    conn.close()

    return render_template("note.html",
                           visit=visit,
                           patient_info=patient_info,
                           admissions=admissions,
                           symptoms=symptoms,
                           treatments=treatments,
                           discharge=discharge)

def upload_notes(p_name, age, diagnosis):
    try:
        conn = get_db_connection()
        sql = "INSERT INTO notes (p_name, age, diagnosis) VALUES (%s, %s, %s)"
        conn.cursor.execute(sql, (p_name, age, diagnosis))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error uploading notes: {e}")

@app.route("/upload", methods=["POST"])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "audio file missing"}), 400
    file = request.files['audio']
    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        uid = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:8]}"
        saved_name = f"{uid}.{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_name)
        file.save(save_path)

        transcript = speech_to_text(save_path)

        # extract structure
        structure = extract_structure_from_transcript(transcript)

        # save result json
        result_obj = {
            "upload_filename": saved_name,
            "transcript": transcript,
            "structure": structure
        }
        result_path = os.path.join(PROCESSED_FOLDER, f"{uid}.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result_obj, f, ensure_ascii=False, indent=2)

        return redirect(url_for("result_view", result_file=f"{uid}.json"))
    else:
        return jsonify({"error": "filetype not allowed"}), 400

@app.route("/results/<result_file>")
def result_view(result_file):
    path = os.path.join(PROCESSED_FOLDER, result_file)
    if not os.path.exists(path):
        return "Result not found", 404
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return render_template("result.html", data=data)

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/processed/<path:filename>")
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
