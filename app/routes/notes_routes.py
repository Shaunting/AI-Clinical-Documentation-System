from flask import Blueprint, render_template
from app.services.db_service import get_conn

bp = Blueprint("notes", __name__)


@bp.route("/notes")
def notes():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT v.visit_id, p.age, p.sex,
                (
                    SELECT a.date 
                    FROM admissions a 
                    WHERE a.visit_id = v.visit_id 
                    ORDER BY a.date DESC LIMIT 1
                ) AS latest_admission_date,
                (
                    SELECT t.related_condition 
                    FROM treatments t 
                    WHERE t.visit_id = v.visit_id 
                    LIMIT 1
                ) AS primary_diagnosis
            FROM visits v
            LEFT JOIN patient_information p 
                ON p.visit_id = v.visit_id
            ORDER BY v.visit_id ASC;
        """)
        notes_list = cursor.fetchall()

    conn.close()
    return render_template("notes.html", notes=notes_list)


@bp.route("/note/<int:visit_id>")
def note_detail(visit_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM visits WHERE visit_id=%s", (visit_id,))
        visit = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM patient_information WHERE visit_id=%s", (visit_id,)
        )
        patient_info = cursor.fetchone()

        cursor.execute("SELECT * FROM admissions WHERE visit_id=%s", (visit_id,))
        admissions = cursor.fetchall()

        cursor.execute("SELECT * FROM symptoms WHERE visit_id=%s", (visit_id,))
        symptoms = cursor.fetchall()

        cursor.execute("SELECT * FROM treatments WHERE visit_id=%s", (visit_id,))
        treatments = cursor.fetchall()

        cursor.execute("SELECT * FROM discharges WHERE visit_id=%s", (visit_id,))
        discharge = cursor.fetchone()

    conn.close()

    return render_template(
        "note.html",
        visit=visit,
        patient_info=patient_info,
        admissions=admissions,
        symptoms=symptoms,
        treatments=treatments,
        discharge=discharge,
    )
