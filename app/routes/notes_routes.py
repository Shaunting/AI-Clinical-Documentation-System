from flask import Blueprint, render_template
from app.services.db_service import get_conn

bp = Blueprint("notes", __name__)


@bp.route("/notes")
def notes():
    conn = get_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
                    SELECT 
                        v.visit_id,
                        p.full_name,
                        p.age,
                        p.sex,
                        v.visit_date,
                        v.visit_reason
                    FROM visit v
                    LEFT JOIN patient p ON v.patient_id = p.patient_id
                    ORDER BY v.visit_id DESC
        """)
        notes_list = cursor.fetchall()

    conn.close()
    return render_template("notes.html", notes=notes_list)


@bp.route("/note/<int:visit_id>")
def note_detail(visit_id):
    conn = get_conn()
    with conn.cursor() as cursor:
        # 1. Visit
        cursor.execute("SELECT * FROM visit WHERE visit_id = %s", (visit_id,))
        visit = cursor.fetchone()

        # 2. Patient
        cursor.execute("SELECT * FROM patient WHERE patient_id = %s", 
                       (visit['patient_id'],))
        patient_info = cursor.fetchone()

        # 3. Patient Medical History
        cursor.execute("SELECT * FROM patient_medical_history WHERE patient_id = %s",
                       (visit['patient_id'],))
        medical_history = cursor.fetchone()

        # 4. Surgeries
        cursor.execute("SELECT * FROM surgeries WHERE patient_id = %s",
                       (visit['patient_id'],))
        surgeries_list = cursor.fetchall()

        # 5. Symptoms
        cursor.execute("SELECT * FROM symptoms WHERE visit_id = %s",
                       (visit_id,))
        symptoms = cursor.fetchall()

        # 6. Treatments
        cursor.execute("SELECT * FROM treatments WHERE visit_id = %s",
                       (visit_id,))
        treatments = cursor.fetchall()

        # 7. Conversation Summary
        cursor.execute("SELECT * FROM conversation_summary WHERE conversation_id = %s",
                       (visit['conversation_id'],))
        final_summary = cursor.fetchone()

    conn.close()

    return render_template(
        "note.html",
        visit=visit,
        patient_info=patient_info,
        medical_history=medical_history,
        surgeries=surgeries_list,
        symptoms=symptoms,
        treatments=treatments,
        final_summary=final_summary,
    )
