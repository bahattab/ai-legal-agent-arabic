import os
import sys
import tempfile

# مجلد بيانات معزول للاختبارات — يجب ضبطه قبل استيراد config
os.environ["HAKAM_DATA_DIR"] = tempfile.mkdtemp(prefix="hakam-test-")
os.environ.setdefault("OPENAI_API_KEY", "test-key-123456789")
os.environ.pop("HAKAM_SETTINGS_JSON", None)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
