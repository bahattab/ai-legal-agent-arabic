"""مشغّل نسخة سطح المكتب لحَكَم.

يشغّل خادم Flask محلياً على منفذ حر (127.0.0.1 فقط) ثم يفتحه في نافذة أصلية عبر pywebview
(WebView2 على Windows). إن تعذّر pywebview يفتح المتصفح الافتراضي ويبقى يعمل حتى إغلاقه من
أيقونة الإيقاف في الواجهة أو من مدير المهام.

البيانات (قاعدة القضايا وإعدادات المزودين) في: %APPDATA%\\Hakam
"""
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

os.environ.setdefault("HAKAM_DESKTOP", "1")  # قبل استيراد config


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url + "/health", timeout=2):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _serve(app, port: int):
    from waitress import serve
    serve(app, host="127.0.0.1", port=port, threads=8, channel_timeout=900, _quiet=True)


def _browser_loop(url: str) -> int:
    webbrowser.open(url)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return 0


def _log_path() -> str:
    from config import DATA_DIR
    return os.path.join(DATA_DIR, "hakam.log")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # نسخة EXE بلا نافذة طرفية: نوجّه المخرجات لملف سجل
    if getattr(sys, "frozen", False) and "--console" not in argv:
        log = open(_log_path(), "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = log

    from app import app
    from version import APP_NAME_AR, __version__

    port = int(os.getenv("HAKAM_DESKTOP_PORT") or _free_port())
    url = f"http://127.0.0.1:{port}"
    threading.Thread(target=_serve, args=(app, port), daemon=True).start()
    if not _wait_until_up(url):
        print("تعذّر تشغيل الخادم المحلي", file=sys.stderr)
        return 1
    print(f"Hakam {__version__} running at {url}")

    if "--smoke-test" in argv:  # يُستخدم في CI للتأكد أن ملف EXE يقلع ويخدم الصفحات
        with urllib.request.urlopen(url + "/settings", timeout=10) as r:
            return 0 if r.status == 200 else 1
    if "--browser" in argv:
        return _browser_loop(url)

    try:
        import webview
    except Exception as e:  # noqa: BLE001
        print(f"pywebview غير متاح ({e})؛ سيُفتح المتصفح", file=sys.stderr)
        return _browser_loop(url)

    webview.create_window(f"{APP_NAME_AR} — الذكاء القانوني السيادي {__version__}", url,
                          width=1280, height=860, min_size=(900, 600), text_select=True)
    try:
        webview.start(private_mode=False)
    except Exception as e:  # noqa: BLE001 — مثلاً WebView2 غير مثبت
        print(f"تعذّر فتح النافذة ({e})؛ سيُفتح المتصفح", file=sys.stderr)
        return _browser_loop(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
