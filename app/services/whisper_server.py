from flask import Flask, request, jsonify
import whisper
import tempfile
import os

app = Flask(__name__)

# Whisper 모델 로드 (tiny/small/base/medium 등 선택)
model = whisper.load_model("base")

@app.route("/upload", methods=["POST"])
def upload():
    # 1) check the consent
    consent = request.form.get("consent", "")
    if consent != "on":
        return jsonify({"error": "Consent not given"}), 400

    # 2) check if there's a file 
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["audio"]

    # 3) save as temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        temp_path = tmp.name
        audio_file.save(temp_path)

    try:
        # 4) Whisper
        result = model.transcribe(temp_path, fp16=False)
        transcript = result.get("text", "")

        return jsonify({
            "text": transcript
        })

    finally:
        # 5) remove the temp
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
