"""خادم حَكَم (Flask) — يعمل كما هو للويب، ويُغلَّف داخل نافذة في نسخة سطح المكتب."""
import asyncio
import hmac
import ipaddress
import os
import socket
from urllib.parse import urlparse

from flask import Flask, abort, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

import settings
from agents import base
from config import (ACCESS_TOKEN, ADMIN_TOKEN, DATA_DIR, DESKTOP_MODE, FLASK_DEBUG, HOST, PORT,
                    RESOURCE_DIR)
from database import (create_conversation, delete_conversation, get_conversation_messages,
                      get_conversations, init_db, save_message)
from pipeline import LegalPipeline
from version import APP_NAME_AR, __version__

app = Flask(__name__, template_folder=os.path.join(RESOURCE_DIR, "templates"),
            static_folder=os.path.join(RESOURCE_DIR, "static"))
app.json.ensure_ascii = False
if not DESKTOP_MODE:
    # خلف بروكسي TLS (Render، cPanel، nginx): نثق بترويسة واحدة لمعرفة https والعنوان الأصلي
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

init_db()


# ---------- الأمان ----------
def _safe_equal(given, expected: str) -> bool:
    """مقارنة ثابتة الزمن لا ترمي استثناء مع النصوص غير ASCII أو القيم غير النصية."""
    if not isinstance(given, str) or not given or not expected:
        return False
    return hmac.compare_digest(given.encode("utf-8"), expected.encode("utf-8"))


def _token_ok(expected: str, *names) -> bool:
    for name in names:
        given = request.headers.get(name) or request.cookies.get(name.lower().replace("-", "_"))
        if _safe_equal(given, expected):
            return True
    return False


def settings_writable() -> bool:
    """سطح المكتب: مسموح دائماً (محلي). الويب: يتطلب HAKAM_ADMIN_TOKEN صحيحاً."""
    if DESKTOP_MODE:
        return True
    return bool(ADMIN_TOKEN) and _token_ok(ADMIN_TOKEN, "X-Admin-Token")


@app.before_request
def desktop_host_guard():
    """سطح المكتب: نقبل فقط Host محلياً، لمنع هجمات DNS rebinding من مواقع خبيثة."""
    if not DESKTOP_MODE:
        return None
    host = (request.host or "").rsplit(":", 1)[0].strip("[]").lower()
    if host not in ("127.0.0.1", "localhost", "::1"):
        abort(403)
    return None


@app.before_request
def access_gate():
    """حماية اختيارية للتطبيق كله على الويب عبر HAKAM_ACCESS_TOKEN."""
    if not ACCESS_TOKEN or DESKTOP_MODE:
        return None
    if request.endpoint in ("static", "health", "unlock", "unlock_page"):
        return None
    if _token_ok(ACCESS_TOKEN, "X-Access-Token"):
        return None
    if request.path.startswith("/api/"):
        return jsonify({"error": "مطلوب رمز الدخول"}), 401
    return render_template("unlock.html", version=__version__), 401


@app.route("/unlock", methods=["POST"], endpoint="unlock")
def unlock():
    token = (request.get_json(silent=True) or {}).get("token", "")
    if not ACCESS_TOKEN or not _safe_equal(token, ACCESS_TOKEN):
        return jsonify({"error": "رمز غير صحيح"}), 403
    resp = jsonify({"ok": True})
    resp.set_cookie("x_access_token", token, httponly=True, samesite="Strict",
                    secure=request.is_secure or os.getenv("HAKAM_COOKIE_SECURE") == "1",
                    max_age=60 * 60 * 24 * 30)
    return resp


@app.after_request
def security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return resp


# ---------- الصفحات ----------
@app.route("/")
def index():
    return render_template("index.html", version=__version__, app_name=APP_NAME_AR)


@app.route("/settings")
def settings_page():
    return render_template("settings.html", version=__version__, desktop=DESKTOP_MODE,
                           admin_required=not DESKTOP_MODE)


@app.route("/health", endpoint="health")
def health():
    return jsonify({"status": "ok", "version": __version__})


@app.route("/api/version")
def version():
    return jsonify({"version": __version__, "desktop": DESKTOP_MODE,
                    "settings_source": settings.source(), "data_dir": DATA_DIR if DESKTOP_MODE else None})


# ---------- المحادثة ----------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    conversation_id = data.get("conversation_id")

    if not question:
        return jsonify({"error": "السؤال مطلوب"}), 400
    if len(question) > 20000:
        return jsonify({"error": "السؤال طويل جداً (الحد 20000 حرف)"}), 400

    if not conversation_id:
        conversation_id = create_conversation(title=question[:50])
    save_message(conversation_id, "user", question)

    try:
        result = asyncio.run(LegalPipeline.process(question))
    except Exception as e:  # noqa: BLE001 — نعيد الخطأ للواجهة بالعربية
        app.logger.exception("pipeline failed")
        return jsonify({"error": f"حدث خطأ أثناء المعالجة: {e}"}), 500

    full_response = f"{result['final_response']['opinion']}\n\n---\n{result['final_response']['disclaimer']}"
    save_message(conversation_id, "assistant", full_response, metadata=result["stages"])
    return jsonify({"conversation_id": conversation_id, "response": full_response,
                    "stages": result["stages"], "final_response": result["final_response"]})


@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    return jsonify(get_conversations())


@app.route("/api/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    return jsonify(get_conversation_messages(conversation_id))


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE"])
def remove_conversation(conversation_id):
    if not settings_writable():
        abort(403)
    delete_conversation(conversation_id)
    return jsonify({"ok": True})


# ---------- الإعدادات والمزودون ----------
@app.route("/api/settings", methods=["GET"])
def get_settings():
    try:
        view = settings.public_view()
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"settings": view, "presets": settings.PRESETS, "roles": settings.AGENT_LABELS_AR,
                    "writable": settings_writable(), "source": settings.source(),
                    "admin_configured": bool(ADMIN_TOKEN), "desktop": DESKTOP_MODE})


@app.route("/api/settings", methods=["PUT"])
def put_settings():
    if not settings_writable():
        return jsonify({"error": "غير مصرح: أدخل رمز المسؤول (HAKAM_ADMIN_TOKEN)"}), 403
    try:
        settings.save(request.get_json(silent=True) or {})
    except (ValueError, PermissionError, TypeError, KeyError) as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"ok": True, "settings": settings.public_view()})


def _blocked_host(url: str) -> bool:
    """على الويب: نمنع عناوين البيانات الوصفية السحابية (169.254.x.x) إلا بإذن صريح."""
    if DESKTOP_MODE or os.getenv("HAKAM_ALLOW_LINK_LOCAL") == "1":
        return False
    host = urlparse(url).hostname or ""
    try:
        addrs = {ai[4][0] for ai in socket.getaddrinfo(host, None)}
    except OSError:
        return False  # سيفشل الاتصال لاحقاً برسالة واضحة
    return any(ipaddress.ip_address(a.split("%")[0]).is_link_local for a in addrs)


def _provider_from_request(body: dict) -> dict:
    """يبني مزوداً للاختبار. المفتاح المحفوظ لا يُستخدم إلا مع نفس Base URL المحفوظ."""
    p = body.get("provider") if isinstance(body, dict) else None
    if not isinstance(p, dict):
        raise ValueError("بيانات المزود غير صالحة")
    p = dict(p)
    if p.get("type") not in settings.PROVIDER_TYPES:
        raise ValueError("نوع مزود غير مدعوم")
    if not str(p.get("base_url", "")).startswith(("http://", "https://")):
        raise ValueError("Base URL غير صالح")
    if _blocked_host(p["base_url"]):
        raise ValueError("هذا العنوان محجوب على نسخة الويب (link-local)")
    key = str(p.get("api_key") or "").strip()
    if not key or key.startswith("••••"):
        saved_id = p.get("original_id") or p.get("id")
        saved = next((x for x in settings.load()["providers"] if x["id"] == saved_id), {})
        p["api_key"] = saved.get("api_key", "") if saved.get("base_url") == p["base_url"] else ""
    p.setdefault("id", "test")
    p.setdefault("name", p["id"])
    return p


@app.route("/api/providers/test", methods=["POST"])
def test_provider():
    if not settings_writable():
        return jsonify({"error": "غير مصرح"}), 403
    body = request.get_json(silent=True) or {}
    try:
        provider = _provider_from_request(body)
        reply = asyncio.run(base.test_provider(provider, body.get("model", "")))
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e)[:400]}), 200
    return jsonify({"ok": True, "reply": reply[:200]})


@app.route("/api/providers/models", methods=["POST"])
def provider_models():
    if not settings_writable():
        return jsonify({"error": "غير مصرح"}), 403
    try:
        models = asyncio.run(base.list_models(_provider_from_request(request.get_json(silent=True) or {})))
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e)[:400]}), 200
    return jsonify({"ok": True, "models": models})


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=HOST, port=PORT)
