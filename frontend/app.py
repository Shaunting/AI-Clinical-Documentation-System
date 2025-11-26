import os
import uuid
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, flash

# 환경설정
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
ALLOWED_EXT = {"webm", "wav", "ogg", "mp3", "m4a"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")  # 실제 배포시에는 강력히 변경

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# ---------- 플레이스홀더: 음성 인식 및 구조 추출 함수들 ----------
def speech_to_text(audio_path):
    """
    실제 구현: Whisper / Google STT / OpenAI API 등으로 대체하세요.
    현재는 파일명을 포함한 더미 텍스트를 반환합니다.
    """
    # TODO: 여기에 실제 STT 호출 코드 추가
    dummy_transcript = f"(더미 전사) 파일: {os.path.basename(audio_path)} - 전사 텍스트 예시입니다."
    return dummy_transcript

def extract_structure_from_transcript(transcript):
    """
    실제 구현: 규칙 기반 파서 / NER / LLM(예: OpenAI) 등으로
    의료 대화에서 필요한 필드(문제, 진단 의심, 약 처방, 추천 검사 등)를 추출하세요.

    여기서는 예시 JSON 구조를 반환합니다.
    """
    # TODO: 여기에 LLM 호출 또는 규칙/모델 적용
    structure = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "transcript_length_chars": len(transcript)
        },
        "participants": ["doctor", "patient"],  # 실제 참가자 분리는 더 정교하게
        "transcript_preview": transcript[:500],
        "extracted": {
            "chief_complaint": "복통 (예시)",
            "history_of_present_illness": "3일 전부터 시작된 통증, 식사 후 악화 (예시)",
            "possible_diagnoses": ["위염 (예시)", "소화불량 (예시)"],
            "recommended_tests": ["혈액검사", "복부초음파"],
            "prescription": [
                {"name": "약A", "dosage": "1일 2회", "notes": "식후 복용 (예시)"}
            ],
            "follow_up": "1주일 후 재진료 권장"
        },
        "confidence": {
            "overall": 0.75
        }
    }
    return structure

# ---------- 라우트 ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/elements")
def elements():
    return render_template("elements.html")

@app.route("/generic")
def generic():
    return render_template("generic.html")

@app.route("/upload", methods=["POST"])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "audio file missing"}), 400
    file = request.files['audio']
    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400
    if file and allowed_file(file.filename):
        # 고유한 파일명 생성
        ext = file.filename.rsplit('.', 1)[1].lower()
        uid = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:8]}"
        saved_name = f"{uid}.{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_name)
        file.save(save_path)

        # 여기에 오디오 변환(예: webm->wav) 필요시 수행
        # 예: pydub로 변환 후 processed 폴더에 저장

        # 1) STT
        transcript = speech_to_text(save_path)

        # 2) 구조 추출
        structure = extract_structure_from_transcript(transcript)

        # 3) 결과 저장(선택)
        result_obj = {
            "upload_filename": saved_name,
            "transcript": transcript,
            "structure": structure
        }
        result_path = os.path.join(PROCESSED_FOLDER, f"{uid}.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result_obj, f, ensure_ascii=False, indent=2)

        # 최종 결과 페이지로 리디렉트하거나 JSON 반환
        return redirect(url_for("result_view", result_file=f"{uid}.json"))
    else:
        return jsonify({"error": "filetype not allowed"}), 400

@app.route("/results/<result_file>")
def result_view(result_file):
    # processed 폴더에서 결과 읽어와 화면으로 렌더링
    path = os.path.join(PROCESSED_FOLDER, result_file)
    if not os.path.exists(path):
        return "Result not found", 404
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 템플릿에서 예쁘게 표시
    return render_template("result.html", data=data)

# 오디오/결과 파일 직접 접근(디버그용). 배포 시에는 인증 필요
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/processed/<path:filename>")
def processed_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
