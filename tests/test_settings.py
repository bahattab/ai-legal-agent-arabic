"""اختبارات إعدادات المزودين وواجهة الإعدادات وصلاحياتها."""
import copy
import json

import pytest

import app as hakam_app
import config
import settings


@pytest.fixture(autouse=True)
def clean_settings_file():
    import os
    if os.path.exists(config.SETTINGS_PATH):
        os.remove(config.SETTINGS_PATH)
    yield
    if os.path.exists(config.SETTINGS_PATH):
        os.remove(config.SETTINGS_PATH)


def multi_provider():
    d = settings.load()
    d["providers"].append({"id": "claude", "name": "Anthropic", "type": "anthropic",
                           "base_url": "https://api.anthropic.com", "api_key": "sk-ant-secret-abcdef"})
    d["agents"]["synthesizer"] = {"provider": "claude", "model": "claude-sonnet-4-5"}
    return d


def test_defaults_from_env():
    d = settings.load()
    assert settings.source() == "defaults"
    assert d["providers"][0]["api_key"] == "env:OPENAI_API_KEY"
    provider, model = settings.agent_target("analyzer")
    assert settings.resolve_key(provider["api_key"]) == "test-key-123456789"


def test_save_masks_and_preserves_keys():
    settings.save(multi_provider())
    view = settings.public_view()
    claude = next(p for p in view["providers"] if p["id"] == "claude")
    assert claude["api_key"].startswith("••••") and "secret" not in json.dumps(view)
    # إعادة الحفظ بالقيمة المخفية يجب أن تحتفظ بالمفتاح الأصلي
    settings.save(copy.deepcopy(view))
    assert settings.agent_target("synthesizer")[0]["api_key"] == "sk-ant-secret-abcdef"
    assert settings.model_name("synthesizer") == "claude/claude-sonnet-4-5"


@pytest.mark.parametrize("mutate,msg", [
    (lambda d: d["providers"][0].update(type="foo"), "نوع مزود"),
    (lambda d: d["providers"][0].update(base_url="ftp://x"), "Base URL"),
    (lambda d: d["agents"]["verifier"].update(provider="ghost"), "غير موجود"),
    (lambda d: d.update(verification_threshold=2), "حد القبول"),
])
def test_validation_errors(mutate, msg):
    d = settings.load()
    mutate(d)
    with pytest.raises(ValueError, match=msg):
        settings.validate(d)


def test_env_json_overrides(monkeypatch):
    d = multi_provider()
    monkeypatch.setenv("HAKAM_SETTINGS_JSON", json.dumps(d))
    assert settings.source() == "env"
    assert settings.model_name("synthesizer") == "claude/claude-sonnet-4-5"
    with pytest.raises(PermissionError):
        settings.save(d)


def client(monkeypatch, desktop=False, admin=""):
    monkeypatch.setattr(hakam_app, "DESKTOP_MODE", desktop)
    monkeypatch.setattr(hakam_app, "ADMIN_TOKEN", admin)
    return hakam_app.app.test_client()


def test_web_settings_readonly_without_admin(monkeypatch):
    c = client(monkeypatch)
    r = c.get("/api/settings")
    assert r.status_code == 200 and r.json["writable"] is False
    assert "test-key" not in r.get_data(as_text=True)
    assert c.put("/api/settings", json=settings.load()).status_code == 403
    assert c.delete("/api/conversations/1").status_code == 403


def test_web_settings_with_admin_token(monkeypatch):
    c = client(monkeypatch, admin="s3cret")
    assert c.put("/api/settings", json=multi_provider(), headers={"X-Admin-Token": "wrong"}).status_code == 403
    r = c.put("/api/settings", json=multi_provider(), headers={"X-Admin-Token": "s3cret"})
    assert r.status_code == 200 and settings.source() == "file"


def test_desktop_settings_writable(monkeypatch):
    c = client(monkeypatch, desktop=True)
    assert c.get("/api/settings").json["writable"] is True
    bad = settings.load(); bad["agents"]["analyzer"]["provider"] = "nope"
    r = c.put("/api/settings", json=bad)
    assert r.status_code == 400 and "غير موجود" in r.json["error"]


def test_access_token_gate(monkeypatch):
    c = client(monkeypatch)
    monkeypatch.setattr(hakam_app, "ACCESS_TOKEN", "door")
    assert c.get("/api/conversations").status_code == 401
    assert c.get("/health").status_code == 200
    assert c.post("/unlock", json={"token": "door"}).status_code == 200
    assert c.get("/api/conversations").status_code == 200  # الكوكي محفوظ في العميل


def test_pages_and_version(monkeypatch):
    c = client(monkeypatch)
    from version import __version__
    assert c.get("/api/version").json["version"] == __version__
    for path in ("/", "/settings"):
        r = c.get(path)
        assert r.status_code == 200 and __version__ in r.get_data(as_text=True)
