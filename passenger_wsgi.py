"""نقطة الدخول لاستضافة cPanel (Setup Python App / Phusion Passenger).

في cPanel: Application startup file = passenger_wsgi.py ، Application Entry point = application
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application  # noqa: E402,F401
