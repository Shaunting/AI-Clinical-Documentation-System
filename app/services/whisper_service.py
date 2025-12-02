import os
import tempfile
import whisper


# Load Whisper once at startup (fast)
# You can change "base" to "small", "medium", or "large"
MODEL_NAME = "base"
_model = whisper.load_model(MODEL_NAME)


def transcribe_audio(file_storage):
    """
    Takes a Werkzeug FileStorage object (from request.files["audio"]),
    saves it temporarily, transcribes with Whisper, then deletes the temp file.

    Returns: transcript (string)
    """

    # Create a temp file with .webm extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        temp_path = tmp.name
        file_storage.save(temp_path)

    try:
        # Whisper transcription
        result = _model.transcribe(temp_path, fp16=False)
        transcript = result.get("text", "")
        return transcript.strip()

    except Exception as e:
        print("Whisper transcription error:", e)
        return ""

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
