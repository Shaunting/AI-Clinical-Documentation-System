from flask import Blueprint, request, jsonify
from app.services.db_service import insert_raw_summary

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/upload-file", methods=["POST"])
def upload_file():
    """
    Accepts a file, stores it in Postgres, returns the row ID.
    """

    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Read the file
    file_bytes = file.read()
    content_type = file.content_type
    filename = file.filename

    # Insert into DB
    row_id = insert_raw_summary(filename, file_bytes, content_type)

    return jsonify({"message": "File uploaded", "file_id": row_id}), 201
