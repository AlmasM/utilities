"""
/translate — translates text to a chosen language.

Open-source options you can use:
  - LibreTranslate: set LIBRE_TRANSLATE_URL (and optional LIBRE_TRANSLATE_API_KEY) to use
    a self-hosted or public instance (https://github.com/LibreTranslate/LibreTranslate).
  - Argos Translate: fully offline; install with pip install argostranslate and language
    packs (https://github.com/argosopentech/argos-translate).
  - OpenNMT / CTranslate2: for custom or self-hosted NMT models.

By default this endpoint uses Google Translate via deep-translator (no API key).
Switch to LibreTranslate by setting LIBRE_TRANSLATE_URL.

POST /translate
  Header:  X-Admin-Key: <your-key>
  Body:    JSON {"text": "<text to translate>", "target_lang": "<code or name>", "source_lang": "<optional, default auto>"}
  Returns: {"success": true, "data": "<translated text>"}
           {"success": false, "message": "<reason>"}

GET /translate/languages
  Returns: {"success": true, "data": [{"name": "...", "code": "..."}, ...]}
"""

import os

from flask import Blueprint, request, jsonify
from deep_translator import GoogleTranslator, LibreTranslator

from utils.auth import require_admin_key

translate_bp = Blueprint("translate", __name__)

LIBRE_URL = os.environ.get("LIBRE_TRANSLATE_URL", "").rstrip("/")
LIBRE_API_KEY = os.environ.get("LIBRE_TRANSLATE_API_KEY", "")


def _translator(source: str, target: str):
    if LIBRE_URL:
        return LibreTranslator(
            source=source,
            target=target,
            base_url=LIBRE_URL,
            api_key=LIBRE_API_KEY or None,
        )
    return GoogleTranslator(source=source, target=target)


@translate_bp.route("/translate/languages", methods=["GET"])
@require_admin_key
def list_languages():
    """Return supported target languages (name + code). Uses Google's list (standard codes)."""
    try:
        langs = GoogleTranslator().get_supported_languages(as_dict=True)
        data = [{"name": name, "code": code} for name, code in sorted(langs.items(), key=lambda x: x[0].lower())]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@translate_bp.route("/translate", methods=["POST"])
@require_admin_key
def translate():
    body = request.get_json(silent=True) or {}
    text = body.get("text") or request.form.get("text")
    target_lang = (body.get("target_lang") or body.get("target") or request.form.get("target_lang") or request.form.get("target") or "").strip()
    source_lang = (body.get("source_lang") or body.get("source") or request.form.get("source_lang") or request.form.get("source") or "auto").strip() or "auto"

    if not text:
        return jsonify({"success": False, "message": "Missing 'text'. Send JSON or form with 'text'."}), 400
    if not target_lang:
        return jsonify({"success": False, "message": "Missing 'target_lang'. Pick a language code or name (e.g. 'es', 'french')."}), 400

    try:
        translator = _translator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return jsonify({"success": True, "data": translated})
    except Exception as e:
        return jsonify({"success": False, "message": f"Translation failed: {str(e)}"}), 500
