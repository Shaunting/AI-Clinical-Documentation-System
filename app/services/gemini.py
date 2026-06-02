from google import genai
from google.genai import types
import os, json

# -----------------------------------------------------------
# GEMINI CLIENT
# -----------------------------------------------------------
def _gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
    return genai.Client(api_key=api_key)


client = None  # lazy init via get_client()


def get_client():
    global client
    if client is None:
        client = _gemini_client()
    return client


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

structured_config = types.GenerateContentConfig(
    tools=[tools],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY",
            allowed_function_names=["generate_structured_clinical_summary"],
        )
    ),
)


# -----------------------------------------------------------
# GEMINI - Generate Structured Summary
# -----------------------------------------------------------
def generate_structured_summary(transcript: str):
    """
    Takes a transcript string and returns structured JSON from Gemini.
    """

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Use the function `generate_structured_clinical_summary` to extract "
            "structured clinical notes from the transcript below. "
            "Return only as a function call.\n\n"
            f"{transcript}"
        ),
        config=structured_config,
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


# -----------------------------------------------------------
# GEMINI - Generate Summary
# -----------------------------------------------------------

summary_config = types.GenerateContentConfig(
    temperature=0.4,
)


def generate_summary(transcript: str):
    """
    Generate a concise clinical summary tailored for medical documentation.
    Provides an 80 to 120-word paragraph capturing key medical details.
    """

    prompt = (
        "Write a concise clinical summary (80 to 120 words) based on the transcript below. "
        "Summarize the patient's chief complaint, symptom characteristics, duration, "
        "medication history, and functional impact. "
        "Do not add information not present in the transcript. "
        "Use clear medical language appropriate for EHR documentation. "
        "Return a single paragraph only.\n\n"
        f"Transcript:\n{transcript}"
    )

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=summary_config,
    )

    # Prefer response.text
    summary = getattr(response, "text", None)

    # Fallback: scrape text from parts
    if not summary:
        parts = response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, "text"):
                summary = part.text
                break

    return {
        "status": "success",
        "summary": summary or "",
    }
