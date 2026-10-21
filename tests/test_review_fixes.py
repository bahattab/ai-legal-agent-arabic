"""اختبارات انحدار لملاحظات المراجعة المستقلة للإصدار 1.0.0."""
import asyncio
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import app as hakam_app
import config
import settings
from agents import base


@pytest.fixture(autouse=True)
def clean():
    if os.path.exists(config.SETTINGS_PATH):
        os.remove(config.SETTINGS_PATH)
    yield
    if os.path.exists(config.SETTINGS_PATH):
        os.remove(config.SETTINGS_PATH)


@pytest.fixture
def stub_server():
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"  # keep-alive: يكشف إعادة استخدام اتصال من حلقة مغلقة

        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            body = json.dumps({"id": "1", "object": "chat.completion", "created": 0, "model": "m",
                               "choices": [{"index": 0, "finish_reason": "stop",
                                            "message": {"role": "assistant", "content": "OK"}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/v1"
    srv.shutdown()


def test_openai_calls_survive_new_event_loops(stub_server):
    """كل طلب Flask يشغّل asyncio.run جديدة؛ يجب ألا يفشل الطلب الثاني بـ Event loop is closed."""
    provider = {"id": "s", "name": "s", "type": "openai", "base_url": stub_server, "api_key": "k"}
    results = [asyncio.run(base.test_provider(provider, "m")) for _ in range(4)]
    assert results == ["OK"] * 4


def _client(monkeypatch, desktop=False, admin=""):
    monkeypatch.setattr(hakam_app, "DESKTOP_MODE", desktop)
    monkeypatch.setattr(hakam_app, "ADMIN_TOKEN", admin)
    return hakam_app.app.test_client()


def test_desktop_rejects_foreign_host(monkeypatch):
    c = _client(monkeypatch, desktop=True)
    assert c.get("/api/settings", headers={"Host": "evil.example:5000"}).status_code == 403
    assert c.get("/api/settings", headers={"Host": "127.0.0.1:5123"}).status_code == 200


def test_non_ascii_or_non_string_tokens_are_403_not_500(monkeypatch):
    c = _client(monkeypatch, admin="s3cret")
    assert c.put("/api/settings", json={}, headers={"X-Admin-Token": "abé"}).status_code == 403
    monkeypatch.setattr(hakam_app, "ACCESS_TOKEN", "door")
    assert c.post("/unlock", json={"token": 123}).status_code == 403
    assert c.post("/unlock", json={"token": "بابٌ"}).status_code == 403


@pytest.mark.parametrize("payload", [{"providers": ["x"]}, {"providers": "x"}, [1, 2],
                                     {"providers": [], "agents": {"analyzer": "x"}}])
def test_malformed_settings_are_400(monkeypatch, payload):
    c = _client(monkeypatch, desktop=True)
    assert c.put("/api/settings", json=payload).status_code == 400


def test_saved_key_not_sent_to_different_base_url(monkeypatch):
    d = settings.load()
    d["providers"][0]["api_key"] = "sk-real-secret-0001"
    settings.save(d)
    view = settings.public_view()
    view["providers"][0]["base_url"] = "https://attacker.example/v1"   # مع المفتاح المخفي
    settings.save(view)
    assert settings.load()["providers"][0]["api_key"] == ""
    # وفي مسار الاختبار
    captured = {}

    async def fake_test(provider, model):
        captured.update(provider)
        return "OK"

    monkeypatch.setattr(base, "test_provider", fake_test)
    c = _client(monkeypatch, desktop=True)
    d = settings.load(); d["providers"][0]["base_url"] = "https://api.openai.com/v1"
    d["providers"][0]["api_key"] = "sk-real-secret-0002"; settings.save(d)
    p = settings.public_view()["providers"][0]
    p["base_url"] = "https://attacker.example/v1"
    c.post("/api/providers/test", json={"provider": p, "model": "m"})
    assert captured.get("api_key") == ""


def test_renaming_provider_id_keeps_key():
    d = settings.load()
    d["providers"][0]["api_key"] = "sk-keep-me-123456"
    settings.save(d)
    view = settings.public_view()
    view["providers"][0]["original_id"] = view["providers"][0]["id"]
    view["providers"][0]["id"] = "main"
    for a in view["agents"].values():
        a["provider"] = "main"
    settings.save(view)
    saved = settings.load()["providers"][0]
    assert saved["id"] == "main" and saved["api_key"] == "sk-keep-me-123456" and "original_id" not in saved


def test_link_local_blocked_on_web(monkeypatch):
    c = _client(monkeypatch, admin="s3cret")
    r = c.post("/api/providers/test", headers={"X-Admin-Token": "s3cret"},
               json={"provider": {"type": "openai", "base_url": "http://169.254.169.254/latest", "api_key": "x"},
                     "model": "m"})
    assert r.json["ok"] is False and "link-local" in r.json["error"]


def test_arabic_json_not_escaped(monkeypatch):
    c = _client(monkeypatch)
    assert "السؤال مطلوب" in c.post("/api/chat", json={}).get_data(as_text=True)
