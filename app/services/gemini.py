from google import genai
from google.genai import types
import os, json

# -----------------------------------------------------------
# GEMINI CLIENT
# -----------------------------------------------------------
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


# -----------------------------------------------------------
# Use functions to specifiy AI Chatbot output (JSON format)
# -----------------------------------------------------------

generate_summary_function = {
    "name": "generate_structured_clinical_summary",
    "description": "Extract and structure a doctor-patient transcript into a structured JSON medical summary aligned with the database schema.",
    "parameters": {
        "type": "object",
        "properties": {
            "visit": {
                "type": "object",
                "properties": {"visit_reason": {"type": "string"}},
                "required": ["visit_reason"],
            },
            "patient": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string"},
                    "age": {"type": "integer"},
                    "sex": {"type": "string"},
                    "race_ethnicity": {"type": "string"},
                    "weight_lb": {"type": "number"},
                    "height_in": {"type": "number"},
                    "occupation": {"type": "string"},
                },
                "required": ["full_name"],
            },
            "patient_medical_history": {
                "type": "object",
                "properties": {
                    "physiological_context": {"type": "string"},
                    "psychological_context": {"type": "string"},
                    "vaccination_history": {"type": "string"},
                    "allergies": {"type": "string"},
                    "exercise_frequency": {"type": "string"},
                    "nutrition": {"type": "string"},
                    "sexual_history": {"type": "string"},
                    "alcohol_consumption": {"type": "string"},
                    "drug_usage": {"type": "string"},
                    "smoking_status": {"type": "string"},
                    "additional_details": {"type": "string"},
                },
            },
            "surgeries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "surgery_reason": {"type": "string"},
                        "surgery_type": {"type": "string"},
                        "procedure_datetime": {
                            "type": "string",
                            "description": "Date and time of the surgical procedure in ISO 8601 format, e.g. 2024-11-15T14:30:00",
                        },
                        "outcome": {"type": "string"},
                        "additional_details": {"type": "string"},
                    },
                },
            },
            "symptoms": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symptom_name": {"type": "string"},
                        "intensity": {"type": "string"},
                        "location": {"type": "string"},
                        "duration": {"type": "string"},
                        "additional_details": {"type": "string"},
                    },
                    "required": ["symptom_name"],
                },
            },
            "treatments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "treatment_name": {"type": "string"},
                        "related_condition": {"type": "string"},
                        "dosage": {"type": "string"},
                        "duration": {"type": "string"},
                        "frequency": {"type": "string"},
                        "reason": {"type": "string"},
                        "reaction": {"type": "string"},
                        "additional_details": {"type": "string"},
                    },
                    "required": ["treatment_name"],
                },
            },
        },
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
# MAIN FUNCTION (this is what routes call)
# -----------------------------------------------------------
def generate_structured_summary(transcript: str):
    """
    Takes a transcript string and returns structured JSON from Gemini.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Use the function `generate_structured_clinical_summary` to extract "
            "structured clinical notes from the transcript below. "
            "Return only as a function call.\n\n"
            f"{transcript}"
        ),
        config=config,
    )

    candidate = response.candidates[0].content.parts[0]

    # If gemini calls the function
    if hasattr(candidate, "function_call") and candidate.function_call:
        fn = candidate.function_call
        return {
            "function": fn.name,
            "structured_output": fn.args,
            "status": "success",
        }

    # If gemini does not call the function
    return {
        "status": "no_function_call",
        "raw_output": response.text,
    }


# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=(
#         "Use the function `generate_structured_clinical_summary` to extract structured clinical notes "
#         "from the transcript below. Return only as a function call, not as text.\n\n"
#         f"{transcript}"
#     ),
#     config=config,
# )

# if response.candidates[0].content.parts[0].function_call:
#     fn = response.candidates[0].content.parts[0].function_call
#     print(f"Function called: {fn.name}")
#     print(json.dumps(fn.args, indent=2))
# else:
#     print("No function call detected.")
#     print(response.text)


# generate_summary_function = {
#     "name": "generate_structured_clinical_summary",
#     "description": "Extract and structure a doctor-patient transcript into a JSON medical summary for EHR documentation.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "visit motivation": {"type": "string"},
#             "admission": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "reason": {"type": "string"},
#                         "date": {"type": "string"},
#                         "duration": {"type": "string"},
#                         "care center details": {"type": "string"},
#                     },
#                 },
#             },
#             "patient information": {
#                 "type": "object",
#                 "properties": {
#                     "age": {"type": "string"},
#                     "sex": {"type": "string"},
#                     "ethnicity": {"type": "string"},
#                     "weight": {"type": "string"},
#                     "height": {"type": "string"},
#                     "family medical history": {"type": "string"},
#                     "recent travels": {"type": "string"},
#                     "socio economic context": {"type": "string"},
#                     "occupation": {"type": "string"},
#                 },
#             },
#             "patient medical history": {
#                 "type": "object",
#                 "properties": {
#                     "physiological context": {"type": "string"},
#                     "psychological context": {"type": "string"},
#                     "vaccination history": {"type": "string"},
#                     "allergies": {"type": "string"},
#                     "exercise frequency": {"type": "string"},
#                     "nutrition": {"type": "string"},
#                     "sexual history": {"type": "string"},
#                     "alcohol consumption": {"type": "string"},
#                     "drug usage": {"type": "string"},
#                     "smoking status": {"type": "string"},
#                 },
#             },
#             "surgeries": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "reason": {"type": "string"},
#                         "Type": {"type": "string"},
#                         "time": {"type": "string"},
#                         "outcome": {"type": "string"},
#                         "details": {"type": "string"},
#                     },
#                 },
#             },
#             "symptoms": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "name of symptom": {"type": "string"},
#                         "intensity of symptom": {"type": "string"},
#                         "location": {"type": "string"},
#                         "time": {"type": "string"},
#                         "temporalisation": {"type": "string"},
#                         "behaviours affecting the symptom": {"type": "string"},
#                         "details": {"type": "string"},
#                     },
#                 },
#             },
#             "medical examinations": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "name": {"type": "string"},
#                         "result": {"type": "string"},
#                         "details": {"type": "string"},
#                     },
#                 },
#             },
#             "diagnosis tests": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "test": {"type": "string"},
#                         "severity": {"type": "string"},
#                         "result": {"type": "string"},
#                         "condition": {"type": "string"},
#                         "time": {"type": "string"},
#                         "details": {"type": "string"},
#                     },
#                 },
#             },
#             "treatments": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "name": {"type": "string"},
#                         "related condition": {"type": "string"},
#                         "dosage": {"type": "string"},
#                         "time": {"type": "string"},
#                         "frequency": {"type": "string"},
#                         "duration": {"type": "string"},
#                         "reason for taking": {"type": "string"},
#                         "reaction to treatment": {"type": "string"},
#                         "details": {"type": "string"},
#                     },
#                 },
#             },
#             "discharge": {
#                 "type": "object",
#                 "properties": {
#                     "reason": {"type": "string"},
#                     "referral": {"type": "string"},
#                     "follow up": {"type": "string"},
#                     "discharge summary": {"type": "string"},
#                 },
#             },
#         },
#         "required": [
#             "visit motivation",
#             "patient information",
#             "patient medical history",
#             "symptoms",
#             "treatments",
#         ],
#     },
# }
