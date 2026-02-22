"""
/health — server status check (no auth required).
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"success": True, "message": "OK"}), 200
