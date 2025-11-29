from google import genai
from google.genai import types
import os, json


# -----------------------------------------------------------
# Configure GEMINI
# -----------------------------------------------------------
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


# -----------------------------------------------------------
# Use functions to specifiy AI Chatbot output (JSON format)
# -----------------------------------------------------------
generate_summary_function = {
    "name": "generate_structured_clinical_summary",
    "description": "Extract and structure a doctor-patient transcript into a JSON medical summary for EHR documentation.",
    "parameters": {
        "type": "object",
        "properties": {
            "visit motivation": {"type": "string"},
            "admission": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"},
                        "date": {"type": "string"},
                        "duration": {"type": "string"},
                        "care center details": {"type": "string"},
                    },
                },
            },
            "patient information": {
                "type": "object",
                "properties": {
                    "age": {"type": "string"},
                    "sex": {"type": "string"},
                    "ethnicity": {"type": "string"},
                    "weight": {"type": "string"},
                    "height": {"type": "string"},
                    "family medical history": {"type": "string"},
                    "recent travels": {"type": "string"},
                    "socio economic context": {"type": "string"},
                    "occupation": {"type": "string"},
                },
            },
            "patient medical history": {
                "type": "object",
                "properties": {
                    "physiological context": {"type": "string"},
                    "psychological context": {"type": "string"},
                    "vaccination history": {"type": "string"},
                    "allergies": {"type": "string"},
                    "exercise frequency": {"type": "string"},
                    "nutrition": {"type": "string"},
                    "sexual history": {"type": "string"},
                    "alcohol consumption": {"type": "string"},
                    "drug usage": {"type": "string"},
                    "smoking status": {"type": "string"},
                },
            },
            "surgeries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string"},
                        "Type": {"type": "string"},
                        "time": {"type": "string"},
                        "outcome": {"type": "string"},
                        "details": {"type": "string"},
                    },
                },
            },
            "symptoms": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name of symptom": {"type": "string"},
                        "intensity of symptom": {"type": "string"},
                        "location": {"type": "string"},
                        "time": {"type": "string"},
                        "temporalisation": {"type": "string"},
                        "behaviours affecting the symptom": {"type": "string"},
                        "details": {"type": "string"},
                    },
                },
            },
            "medical examinations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "result": {"type": "string"},
                        "details": {"type": "string"},
                    },
                },
            },
            "diagnosis tests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "test": {"type": "string"},
                        "severity": {"type": "string"},
                        "result": {"type": "string"},
                        "condition": {"type": "string"},
                        "time": {"type": "string"},
                        "details": {"type": "string"},
                    },
                },
            },
            "treatments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "related condition": {"type": "string"},
                        "dosage": {"type": "string"},
                        "time": {"type": "string"},
                        "frequency": {"type": "string"},
                        "duration": {"type": "string"},
                        "reason for taking": {"type": "string"},
                        "reaction to treatment": {"type": "string"},
                        "details": {"type": "string"},
                    },
                },
            },
            "discharge": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                    "referral": {"type": "string"},
                    "follow up": {"type": "string"},
                    "discharge summary": {"type": "string"},
                },
            },
        },
        "required": [
            "visit motivation",
            "patient information",
            "patient medical history",
            "symptoms",
            "treatments",
        ],
    },
}


tools = types.Tool(function_declarations=[generate_summary_function])

config = types.GenerateContentConfig(
    tools=[tools],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY",
            allowed_function_names=["generate_structured_clinical_summary"],
        )
    ),
)


# -----------------------------------------------------------
# Input transcript in prompt
# -----------------------------------------------------------
transcript = """Doctor: Good morning, what brings you to the Outpatient department today?
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
# Response: Ask ChatGPT
# -----------------------------------------------------------
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "Use the function `generate_structured_clinical_summary` to extract structured clinical notes "
        "from the transcript below. Return only as a function call, not as text.\n\n"
        f"{transcript}"
    ),
    config=config,
)

if response.candidates[0].content.parts[0].function_call:
    fn = response.candidates[0].content.parts[0].function_call
    print(f"Function called: {fn.name}")
    print(json.dumps(fn.args, indent=2))
else:
    print("No function call detected.")
    print(response.text)
