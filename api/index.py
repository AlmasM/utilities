"""
Vercel entry point — imports the Flask app from the root app factory.
Vercel looks for `app` in this file.
"""

from app import create_app

app = create_app()
