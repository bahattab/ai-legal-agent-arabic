# نشر نسخة الويب على أي استضافة

حَكَم تطبيق Python (Flask) عادي، فيعمل على أي استضافة تدعم Python 3.10+ أو Docker. نزّل `hakam-web-<الإصدار>.zip` من صفحة [الإصدارات](https://github.com/bahattab/ai-legal-agent-arabic/releases)، أو استنسخ المستودع.

## قبل أي نشر: ثلاثة متغيرات
| المتغير | لماذا |
|---|---|
| `OPENAI_API_KEY` (أو مفتاح مزودك) | لكي تعمل النماذج. يمكن بدلاً منه ضبط المزودين من صفحة الإعدادات |
| `HAKAM_ADMIN_TOKEN` | رمز طويل عشوائي يفتح صفحة `/settings`. **بدونه تبقى الإعدادات للقراءة فقط** |
| `HAKAM_ACCESS_TOKEN` | يحمي الموقع كله بصفحة دخول. **اضبطه في أي نشر عام**: بدونه يستطيع أي زائر طرح أسئلة على حسابك وقراءة أرشيف القضايا |

> قاعدة البيانات وملف المزودين يُحفظان في `HAKAM_DATA_DIR` (الافتراضي `data/`). على المنصات ذات الأقراص المؤقتة اربطه بقرص دائم، وإلا ضاع الأرشيف والإعدادات عند إعادة التشغيل.

---

## 1. Docker (أي خادم VPS، Railway، Fly.io، Coolify، Dokploy…)
```bash
cp .env.example .env      # ضع المفاتيح والرموز
docker compose up -d --build
# أو بدون compose:
docker build -t hakam:1.0.0 .
docker run -d -p 8000:8000 --env-file .env -v hakam-data:/data hakam:1.0.0
```
افتح `http://الخادم:8000`. الصورة تشغّل gunicorn بعاملين وأربعة خيوط ومهلة 900 ثانية، وفيها فحص صحة على `/health`.

## 2. Render
1. New → **Blueprint** → اختر المستودع. الملف `render.yaml` ينشئ الخدمة وقرصاً دائماً على `/data` ويولّد `HAKAM_ADMIN_TOKEN` و`HAKAM_ACCESS_TOKEN` تلقائياً.
2. أدخل `OPENAI_API_KEY` عند الطلب، ثم انسخ الرمزين من لوحة Environment: رمز الدخول للموقع، ورمز المسؤول لصفحة الإعدادات.
3. إن ظهر خطأ صلاحيات عند الكتابة في `/data` في أول نشر، فأضف في Render متغير `HAKAM_DATA_DIR=/tmp/hakam` مؤقتاً للتشخيص، وتواصل مع دعم Render بخصوص ملكية القرص.

## 3. Heroku وما يشبهها (Procfile)
```bash
heroku create
heroku config:set OPENAI_API_KEY=... HAKAM_ADMIN_TOKEN=...
git push heroku main
```
`Procfile` و`runtime.txt` جاهزان. نظام ملفات Heroku مؤقت: استخدم `HAKAM_SETTINGS_JSON` للإعدادات بدل صفحة الإعدادات (انظر [PROVIDERS.md](PROVIDERS.md)).

## 4. استضافة cPanel المشتركة (Setup Python App)
1. ارفع محتوى الحزمة إلى مجلد مثل `~/hakam`.
2. في cPanel: **Setup Python App** → Create Application:
   - Python version: 3.10 أو أحدث
   - Application root: `hakam`
   - Application URL: النطاق أو المسار المطلوب
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
3. من نفس الصفحة: **Run Pip Install** على `requirements.txt` (أو من الطرفية: `pip install -r requirements.txt`).
4. أضف متغيرات البيئة (`OPENAI_API_KEY`، `HAKAM_ADMIN_TOKEN`) من قسم Environment variables ثم **Restart**.

> بعض الاستضافات المشتركة تقطع الطلبات بعد 30–60 ثانية؛ والسؤال الواحد قد يحتاج أكثر. إن ظهرت أخطاء مهلة فاختر نماذج أسرع للوكلاء أو انتقل إلى VPS/Docker.

## 5. PythonAnywhere
1. ارفع الملفات وأنشئ virtualenv وثبّت `requirements.txt`.
2. Web → Add a new web app → Manual configuration، ثم في ملف WSGI:
   ```python
   import sys; sys.path.insert(0, "/home/USERNAME/hakam")
   from app import app as application
   ```
3. أضف المتغيرات في أول ملف WSGI (`os.environ["OPENAI_API_KEY"] = "..."`) أو في `.env` داخل المجلد.

## 6. خادم Linux مباشرة (systemd + nginx)
```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/gunicorn wsgi:app --bind 127.0.0.1:8000 --workers 2 --threads 4 --timeout 900
```
وحدة systemd مختصرة (`/etc/systemd/system/hakam.service`):
```ini
[Service]
WorkingDirectory=/opt/hakam
EnvironmentFile=/opt/hakam/.env
ExecStart=/opt/hakam/venv/bin/gunicorn wsgi:app --bind 127.0.0.1:8000 --workers 2 --threads 4 --timeout 900
Restart=always
User=hakam
[Install]
WantedBy=multi-user.target
```
وفي nginx اجعل `proxy_read_timeout 900s;` لأن المداولة قد تستغرق أكثر من دقيقة.

## 7. Windows Server / IIS
```powershell
pip install -r requirements.txt
waitress-serve --host 0.0.0.0 --port 8000 --channel-timeout 900 wsgi:app
```

---

## بعد النشر
1. افتح `/health` — يجب أن يعيد `{"status":"ok","version":"1.0.0"}`.
2. افتح `/settings`، أدخل `HAKAM_ADMIN_TOKEN`، أضف مزودك، اضغط **اختبار الاتصال**، ثم **حفظ**.
3. اطرح سؤالاً تجريبياً من الصفحة الرئيسية.

## ملاحظات أمنية
- اجعل الموقع خلف HTTPS دائماً (معظم المنصات توفره تلقائياً).
- المفاتيح المحفوظة من الواجهة تُكتب في `providers.json` داخل مجلد البيانات (صلاحية 600 على Linux). لعزل أقوى استخدم `env:اسم_المتغير` بدل المفتاح.
- حذف القضايا وتعديل الإعدادات يتطلبان رمز المسؤول على الويب.
- اختبار المزودين من صفحة الإعدادات يحجب عناوين link-local (مثل 169.254.169.254 للبيانات الوصفية السحابية). للسماح بها: `HAKAM_ALLOW_LINK_LOCAL=1`.
- المفتاح المحفوظ لا يُرسل إلا إلى نفس Base URL الذي حُفظ معه؛ تغيير العنوان يتطلب إدخال المفتاح من جديد.
- إن كان الموقع خلف بروكسي لا يمرّر `X-Forwarded-Proto` فاضبط `HAKAM_COOKIE_SECURE=1` لتُرسل كوكي الدخول عبر HTTPS فقط.
