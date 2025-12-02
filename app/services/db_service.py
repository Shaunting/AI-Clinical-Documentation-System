import os
import json
import psycopg
from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------------
# Core connection helper
# --------------------------------------------------------
def get_conn():
    return psycopg.connect(
        os.getenv("DATABASE_URL"),
        autocommit=True,
        row_factory=psycopg.rows.dict_row,
    )


# --------------------------------------------------------
# Insert conversation
# --------------------------------------------------------
def insert_conversation(transcript: str) -> int:
    sql = """
        INSERT INTO conversation (raw_text)
        VALUES (%s)
        RETURNING conversation_id;
    """

    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (transcript,))
            row = cur.fetchone()

    conn.close()
    return row["conversation_id"]


# --------------------------------------------------------
# Insert conversation
# --------------------------------------------------------
def insert_conversation_summary(conversation_id: int, summary: str) -> int:
    if isinstance(summary, dict):
        summary = summary.get("summary", "")

    sql = """
        INSERT INTO conversation_summary (conversation_id, summary_text)
        VALUES (%s, %s)
        RETURNING summary_id;
    """

    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, (conversation_id, summary))
            row = cur.fetchone()

    conn.close()
    return row["summary_id"]


# --------------------------------------------------------
# Insert raw summary JSON
# --------------------------------------------------------
def insert_raw_summary(
    conversation_id: int, transcript: str, structured_json: dict
) -> int:
    sql = """
        INSERT INTO structured_summary_raw (conversation_id, transcript, summary_json)
        VALUES (%s, %s, %s)
        RETURNING id;
    """

    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (conversation_id, transcript, json.dumps(structured_json)),
            )
            row_id = cur.fetchone()["id"]

    conn.close()
    return row_id


# ========================================================
# NORMALIZATION FUNCTIONS (ALL SYNCHRONOUS NOW)
# ========================================================


def insert_patient(cur, patient):
    sql = """
        INSERT INTO patient (
            full_name, age, sex, race_ethnicity,
            weight_lb, height_in, occupation
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        RETURNING patient_id;
    """

    cur.execute(
        sql,
        (
            patient.get("full_name"),
            patient.get("age"),
            patient.get("sex"),
            patient.get("race_ethnicity"),
            patient.get("weight_lb"),
            patient.get("height_in"),
            patient.get("occupation"),
        ),
    )
    return cur.fetchone()["patient_id"]


def insert_visit(cur, visit_data, patient_id, conversation_id, doctor_id=None):
    sql = """
        INSERT INTO visit (
            visit_reason, doctor_id, patient_id, conversation_id
        )
        VALUES (%s,%s,%s,%s)
        RETURNING visit_id;
    """

    cur.execute(
        sql,
        (
            visit_data.get("visit_reason"),
            doctor_id,
            patient_id,
            conversation_id,
        ),
    )
    return cur.fetchone()["visit_id"]


def insert_patient_history(cur, patient_id, history):
    if not history or not any(history.values()):
        return

    sql = """
        INSERT INTO patient_medical_history (
            patient_id, physiological_context, psychological_context,
            vaccination_history, allergies, exercise_frequency,
            nutrition, sexual_history, alcohol_consumption,
            drug_usage, smoking_status, additional_details
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """

    cur.execute(
        sql,
        (
            patient_id,
            history.get("physiological_context"),
            history.get("psychological_context"),
            history.get("vaccination_history"),
            history.get("allergies"),
            history.get("exercise_frequency"),
            history.get("nutrition"),
            history.get("sexual_history"),
            history.get("alcohol_consumption"),
            history.get("drug_usage"),
            history.get("smoking_status"),
            history.get("additional_details"),
        ),
    )


def insert_surgeries(cur, patient_id, surgeries):
    if not surgeries:
        return

    sql = """
        INSERT INTO surgeries (
            patient_id, surgery_reason, surgery_type,
            procedure_datetime, outcome, additional_details
        )
        VALUES (%s,%s,%s,%s,%s,%s);
    """

    for s in surgeries:
        cur.execute(
            sql,
            (
                patient_id,
                s.get("surgery_reason"),
                s.get("surgery_type"),
                s.get("procedure_datetime"),
                s.get("outcome"),
                s.get("additional_details"),
            ),
        )


def insert_symptoms(cur, visit_id, symptoms):
    if not symptoms:
        return

    sql = """
        INSERT INTO symptoms (
            visit_id, symptom_name, intensity,
            location, duration, additional_details
        )
        VALUES (%s,%s,%s,%s,%s,%s);
    """

    for sym in symptoms:
        cur.execute(
            sql,
            (
                visit_id,
                sym.get("symptom_name"),
                sym.get("intensity"),
                sym.get("location"),
                sym.get("duration"),
                sym.get("additional_details"),
            ),
        )


def insert_treatments(cur, visit_id, treatments):
    if not treatments:
        return

    sql = """
        INSERT INTO treatments (
            visit_id, treatment_name, related_condition,
            dosage, duration, frequency,
            reason, reaction, additional_details
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """

    for t in treatments:
        cur.execute(
            sql,
            (
                visit_id,
                t.get("treatment_name"),
                t.get("related_condition"),
                t.get("dosage"),
                t.get("duration"),
                t.get("frequency"),
                t.get("reason"),
                t.get("reaction"),
                t.get("additional_details"),
            ),
        )


# --------------------------------------------------------
# Main orchestrator (synchronous)
# --------------------------------------------------------
def insert_normalize_summary(conversation_id, structured_id, summary_json):
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            visit_data = summary_json.get("visit", {})
            patient_data = summary_json.get("patient", {})
            history_data = summary_json.get("patient_medical_history", {})
            surgeries_data = summary_json.get("surgeries", [])
            symptoms_data = summary_json.get("symptoms", [])
            treatments_data = summary_json.get("treatments", [])

            # Insert patient
            patient_id = insert_patient(cur, patient_data)

            # Insert visit
            visit_id = insert_visit(cur, visit_data, patient_id, conversation_id)

            # Insert related tables
            insert_patient_history(cur, patient_id, history_data)
            insert_surgeries(cur, patient_id, surgeries_data)
            insert_symptoms(cur, visit_id, symptoms_data)
            insert_treatments(cur, visit_id, treatments_data)

            return {
                "conversation_id": conversation_id,
                "structured_summary_raw_id": structured_id,
                "patient_id": patient_id,
                "visit_id": visit_id,
            }
