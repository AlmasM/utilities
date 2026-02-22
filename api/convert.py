"""
/convert — converts an uploaded file to Markdown using markitdown.

POST /convert
  Header:  X-Admin-Key: <your-key>
  Body:    multipart/form-data, field name "file"
  Returns: {"success": true, "data": "<markdown>"}
           {"success": false, "message": "<reason>"}
"""

import os
import tempfile

from flask import Blueprint, request, jsonify
from markitdown import MarkItDown

from utils.auth import require_admin_key

convert_bp = Blueprint("convert", __name__)

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls",
    "html", "htm", "txt", "md", "csv", "json", "xml", "zip",
}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@convert_bp.route("/convert", methods=["POST"])
@require_admin_key
def convert():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part in request. Use field name 'file'."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": f"Unsupported file type. Allowed: {sorted(ALLOWED_EXTENSIONS)}"}), 415

    suffix = "." + file.filename.rsplit(".", 1)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
        file.save(tmp_path)

    try:
        md = MarkItDown(enable_plugins=False)
        result = md.convert(tmp_path)
        markdown_text = result.text_content
    except Exception as e:
        return jsonify({"success": False, "message": f"Conversion failed: {str(e)}"}), 500
    finally:
        os.unlink(tmp_path)

    return jsonify({"success": True, "data": markdown_text})
