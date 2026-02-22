"""
/detect — object detection on an image using Ultralytics YOLO.

POST /detect
  Header:  X-Admin-Key: <your-key>
  Body:    multipart/form-data, field name "file" (image)
           OR JSON/form: "url" (image URL)
  Query:   optional "model" (e.g. yolo11n.pt, yolov8n.pt)
  Returns: {"success": true, "data": {"detections": [...], "names": {...}}}
           {"success": false, "message": "<reason>"}

Uses Ultralytics predict: https://docs.ultralytics.com/usage/python/#predict
"""

import os
import tempfile

from flask import Blueprint, request, jsonify
from ultralytics import YOLO

from utils.auth import require_admin_key

detect_bp = Blueprint("detect", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_model_path():
    """Default model path: api/image/models/yolo11n.pt. Override with env DETECT_MODEL (path or name)."""
    default = os.path.join(os.path.dirname(__file__), "models", "yolo11n.pt")
    return os.environ.get("DETECT_MODEL", default)


def _get_model():
    return YOLO(_get_model_path())


@detect_bp.route("/detect", methods=["POST"])
@require_admin_key
def detect():
    # Optional model override from query or form
    model_name = (
        request.args.get("model")
        or (request.get_json(silent=True) or {}).get("model")
        or (request.form.get("model"))
    )
    source = None
    temp_path = None

    # Prefer file upload, then URL
    if "file" in request.files and request.files["file"].filename:
        file = request.files["file"]
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Unsupported image type. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
                    }
                ),
                415,
            )
        suffix = "." + file.filename.rsplit(".", 1)[1].lower()
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_path = tmp.name
        file.save(tmp_path)
        source = temp_path
    else:
        body = request.get_json(silent=True) or {}
        url = body.get("url") or request.form.get("url")
        if url:
            source = url.strip()
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "No image provided. Use multipart field 'file' or JSON/form 'url'.",
                    }
                ),
                400,
            )

    try:
        model = YOLO(model_name) if model_name else _get_model()
        # predict returns a list of Results (one per image)
        results = model.predict(source=source, verbose=False)

        detections_list = []
        names = None

        for result in results:
            # Class names map (id -> name)
            if result.names is not None and names is None:
                names = result.names

            # Detection boxes (xyxy, conf, cls)
            if result.boxes is not None:
                xyxy = result.boxes.xyxy.cpu().numpy().tolist()
                conf = result.boxes.conf.cpu().numpy().tolist()
                cls_ids = result.boxes.cls.cpu().numpy().astype(int).tolist()
                for i in range(len(cls_ids)):
                    detections_list.append(
                        {
                            "box_xyxy": xyxy[i],
                            "confidence": round(float(conf[i]), 4),
                            "class_id": cls_ids[i],
                            "class_name": (result.names or {}).get(cls_ids[i], f"class_{cls_ids[i]}"),
                        }
                    )

        return jsonify(
            {
                "success": True,
                "data": {
                    "detections": detections_list,
                    "names": names or {},
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if temp_path and os.path.isfile(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass
