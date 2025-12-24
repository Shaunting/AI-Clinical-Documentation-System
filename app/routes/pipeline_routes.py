from flask import Blueprint, request, jsonify, current_app
from app.services.whisper_service import transcribe_audio

import os
from app.services.gemini import generate_structured_summary, generate_summary
from app.services.db_service import (
    insert_raw_summary,
    insert_normalize_summary,
    insert_conversation,
    insert_conversation_summary,
)


bp = Blueprint("pipeline", __name__, url_prefix="/pipeline")

# -----------------------------------------------------------
# Test transcript
# -----------------------------------------------------------
test_transcript = """Doctor: Good morning, what brings you to the Outpatient department today?
Patient: Good morning doctor, I have some discomfort in my neck and lower back, and I'm not able to maintain an erect posture.
Doctor: Hmm, okay. Can you tell me more about the discomfort?
Patient: Yes, I tend to fall on either side when I stand up from a sitting position, and my head is always turned to the right and upwards.
Doctor: I see. Are you experiencing any pain in your neck?
Patient: Yes, I have pain and discomfort in my neck.
Doctor: Okay. And what about your back?
Patient: There is a sideways bending in my lumbar region. To counter the abnormal positioning of my back and neck, I have to keep my limbs in a specific position to allow my body weight to be supported.
Doctor: I understand. Does this restriction of body movements affect your daily life?
Patient: Yes, I need assistance in standing and walking, and my parents have to help me with my daily chores, including all activities of self-care.
Doctor: I see. How long have you been experiencing these difficulties?
Patient: I've been experiencing these difficulties for the past four months since I was introduced to olanzapine tablets for the control of my exacerbated mental illness.
Doctor: I see. And you've been diagnosed with bipolar affective disorder, correct?
Patient: Yes, I was diagnosed with bipolar affective disorder seven years ago.
Doctor: And you've been taking olanzapine for your mental illness for seven years, correct?
Patient: Yes, I have. My first episode of the affective disorder was mania when I was eleven, and I've been taking olanzapine tablets in 2.5-10 mg doses per day at different times.
Doctor: I see. So, you developed pain and discomfort in your neck within the second week of being put on olanzapine at a dose of 5 mg per day, correct?
Patient: Yes, that's correct. The sustained and abnormal contraction of my neck muscles pulls my head to the right in an upward direction.
Doctor: I see. And these features have persisted for the first three years of your illness with a varying intensity, distress, and dysfunction, correct?
Patient: Yes, that's correct. The intensity, distress, and dysfunction tend to correlate with the dose of olanzapine.
Doctor: I see. And apart from a brief period of around three weeks when you were given trihexyphenidyl 4 mg per day for rigidity in your upper limbs, you were not prescribed any other psychotropic medication, correct?
Patient: Yes, that's correct. The rigidity showed good response to trihexyphenidyl 4 mg per day.
Doctor: Okay. I'm going to order some tests for you, and I'll be able to give you a proper diagnosis after that.
Patient: Okay, doctor. 
Doctor: I'll also instruct you on follow-up requirements.
Patient: Okay, thank you, doctor."""


transcript_no_roles = """
Good morning, what brings you to the Outpatient department today?
Good morning, I have some discomfort in my neck and lower back, and I'm not able to maintain an erect posture.

Please tell my about yourself.
I'm 27, female, asian, and my name is sarah. I'm 150lbs and 5 foot 7. 

Hmm, okay. Can you tell me more about the discomfort?
I tend to fall on either side when I stand up from a sitting position, and my head is always turned to the right and upwards.

Are you experiencing any pain in your neck?
Yes, I have pain and discomfort in my neck.

Okay. And what about your back?
There is a sideways bending in my lumbar region. To counter the abnormal positioning of my back and neck, I have to keep my limbs in a specific position to allow my body weight to be supported.

Does this restriction of body movements affect your daily life?
Yes, I need assistance in standing and walking, and my parents have to help me with my daily chores, including all activities of self-care.

How long have you been experiencing these difficulties?
I've been experiencing these difficulties for the past four months since I was introduced to olanzapine tablets for the control of my exacerbated mental illness.

And you've been diagnosed with bipolar affective disorder, correct?
Yes, I was diagnosed with bipolar affective disorder seven years ago.

And you've been taking olanzapine for your mental illness for seven years, correct?
Yes. My first episode of the affective disorder was mania when I was eleven, and I've been taking olanzapine tablets in 2.5-10 mg doses per day at different times.

So, you developed pain and discomfort in your neck within the second week of being put on olanzapine at a dose of 5 mg per day, correct?
Yes, that's correct. The sustained and abnormal contraction of my neck muscles pulls my head to the right in an upward direction.

And these features have persisted for the first three years of your illness with varying intensity, distress, and dysfunction, correct?
Yes, the intensity, distress, and dysfunction tend to correlate with the dose of olanzapine.

Apart from a brief period of around three weeks when you were given trihexyphenidyl 4 mg per day for rigidity in your upper limbs, you were not prescribed any other psychotropic medication, correct?
Yes, that's correct. The rigidity showed good response to trihexyphenidyl 4 mg per day.

I'm going to order some tests and then I'll be able to give you a proper diagnosis.
Okay.

I'll also instruct you on follow-up requirements.
Okay, thank you.
"""


# -----------------------------------------------------------
# Input transcript in prompt
# -----------------------------------------------------------
@bp.route("/generate_json", methods=["GET"])
def generate_json_route():
    transcript = transcript_no_roles

    result = generate_structured_summary(transcript)

    return jsonify(result)


@bp.route("/generate_summary", methods=["GET"])
def generate_summary_route():
    transcript = transcript_no_roles

    result = generate_summary(transcript)

    return result


@bp.route("/upload", methods=["POST"])
def upload_audio():
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio uploaded"}), 400

    transcript = transcribe_audio(audio_file)

    print("\n=== TRANSCRIPT START ===")
    print(transcript)
    print("=== TRANSCRIPT END ===\n")

    return jsonify({"status": "ok", "transcript": transcript})


# @bp.route("/upload", methods=["POST"])
# def upload_audio_test():
#     audio_file = request.files.get("audio")

#     if not audio_file:
#         return {"error": "No audio uploaded"}, 400

#     # Save into the uploads folder inside your project
#     upload_folder = current_app.config["UPLOAD_FOLDER"]
#     save_path = os.path.join(upload_folder, audio_file.filename)

#     audio_file.save(save_path)

#     return {
#         "status": "ok",
#         "message": "Audio received successfully",
#         "saved_to": save_path,
#         "filename": audio_file.filename,
#         "content_type": audio_file.content_type,
#     }


@bp.route("/process", methods=["POST"])
def pipeline_process():
    # -----------------------------------------
    # 1. Voice to transcript (Whisper)
    # -----------------------------------------
    print("Transcribing conversation...")
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio uploaded"}), 400

    transcript = transcribe_audio(audio_file)
    if not transcript.strip():
        return jsonify({"error": "Transcription failed"}), 400

    # -----------------------------------------
    # 2. Insert conversation text
    # -----------------------------------------
    print("Inserting conversation...")
    conversation_id = insert_conversation(transcript)

    # -----------------------------------------
    # 3. Generate summary (text-only)
    # -----------------------------------------
    print("Generating conversation summary...")
    summary_dict = generate_summary(transcript)
    summary_text = summary_dict.get("summary", "")

    print("Inserting conversation summary...")
    summary_id = insert_conversation_summary(conversation_id, summary_text)

    # -----------------------------------------
    # 4. Generate structured JSON summary
    # -----------------------------------------
    print("Generating structured JSON summary...")
    structured_json = generate_structured_summary(transcript)

    # -----------------------------------------
    # 5. Insert structured JSON into database
    # -----------------------------------------
    print("Inserting raw summary...")
    structured_id = insert_raw_summary(
        conversation_id=conversation_id,
        transcript=transcript,
        structured_json=structured_json,
    )

    # -----------------------------------------
    # 6. Insert normalized tables
    # -----------------------------------------
    print("Inserting normalized tables...")
    structured_output = structured_json.get("structured_output") or {}

    normalized = insert_normalize_summary(
        conversation_id, structured_id, structured_output
    )

    return jsonify(
        {
            "success": True,
            "conversation_id": conversation_id,
            "summary_id": summary_id,
            "structured_id": structured_id,
            "normalized": normalized,
        }
    )
