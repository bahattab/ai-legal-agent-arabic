"""نقطة دخول WSGI لخوادم الإنتاج: gunicorn wsgi:app  /  waitress-serve wsgi:app"""
from app import app  # noqa: F401
