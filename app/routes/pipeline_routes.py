from flask import Blueprint, jsonify
from app.services.gemini import generate_structured_summary
from app.services.db_service import (
    insert_raw_summary,
    insert_normalize_summary,
    insert_conversation,
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


# -----------------------------------------------------------
# Input transcript in prompt
# -----------------------------------------------------------
@bp.route("/generate", methods=["GET"])
def generate_summary_route():
    transcript = test_transcript

    result = generate_structured_summary(transcript)

    return jsonify(result)


# @bp.route("/process", methods=["POST", "GET"])
# def pipeline_process():
#     # -----------------------------------------
#     # 1. Voice to transcript(text)
#     # -----------------------------------------
#     transcript = test_transcript

#     # -----------------------------------------
#     # 2. Voice to transcript(text)
#     # -----------------------------------------
#     conversation = insert_conversation(transcript)

#     # -----------------------------------------
#     # 3. Generate structured summary JSON
#     # -----------------------------------------
#     structured_json = generate_structured_summary(transcript)

#     # -----------------------------------------
#     # 4. Insert raw summary record into Postgres
#     # -----------------------------------------

#     summary_id = insert_raw_summary(
#         conversation_id=conversation,
#         transcript=transcript,
#         structured_json=structured_json,
#     )

#     # -----------------------------------------
#     # 4. Insert normalized table records into Postgres
#     # -----------------------------------------

#     normalized = insert_normalize_summary(pool, conversation, transcript_text, structured_json)
#     # Return to client
#     return jsonify(
#         {"success": True, "summary_id": summary_id, "structured_json": structured_json}
#     )


@bp.route("/process", methods=["POST", "GET"])
def pipeline_process():
    # -----------------------------------------
    # 1. Voice to transcript(text)
    # -----------------------------------------
    transcript = test_transcript

    # -----------------------------------------
    # 2. Insert conversation into database
    # -----------------------------------------
    print("inserting conversation............")
    conversation_id = insert_conversation(transcript)

    # -----------------------------------------
    # 3. Generate structured json summary
    # -----------------------------------------
    print("structured to json summary............")
    structured_json = generate_structured_summary(transcript)

    # -----------------------------------------
    # 4. Insert json summary into database
    # -----------------------------------------
    print("insert raw summary............")
    structured_id = insert_raw_summary(
        conversation_id=conversation_id,
        transcript=transcript,
        structured_json=structured_json,
    )

    # -----------------------------------------
    # 5. Insert tables from json structured output
    # -----------------------------------------
    print("insert normalized tables............")
    structured_output = structured_json.get("structured_output", {})
    normalized = insert_normalize_summary(
        conversation_id, structured_id, structured_output
    )

    return jsonify(
        {
            "success": True,
            "conversation_id": conversation_id,
            "structured_id": structured_id,
            "normalized": normalized,
        }
    )
