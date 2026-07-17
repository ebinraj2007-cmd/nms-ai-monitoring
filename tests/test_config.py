"""Guards: no hardcoded secrets, config is env-driven, every HTTP call has a timeout."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ai-engine"))


def _py_files():
    return [p for p in ROOT.rglob("*.py")
            if "__pycache__" not in str(p) and "/tests/" not in str(p).replace("\\", "/")]


def test_no_hardcoded_gmail_password():
    pat = re.compile(r'["\'][a-z]{4}\s[a-z]{4}\s[a-z]{4}\s[a-z]{4}["\']')
    for p in _py_files():
        assert not pat.search(p.read_text()), f"possible hardcoded secret in {p}"


def test_no_assigned_password_literal():
    for p in _py_files():
        for line in p.read_text().splitlines():
            if "APP_PASSWORD" in line and "=" in line and "os.environ" not in line \
               and "get(" not in line and "def " not in line:
                assert not re.search(r'=\s*["\'][^"\']+["\']', line), f"secret literal in {p}: {line}"


def test_alert_reads_password_from_env(monkeypatch):
    monkeypatch.setenv("NMS_GMAIL_APP_PASSWORD", "from-env-not-source")
    monkeypatch.setenv("NMS_GMAIL_ADDRESS", "x@y.com")
    import importlib, alert
    importlib.reload(alert)
    assert alert.GMAIL_APP_PASSWORD == "from-env-not-source"


def test_all_requests_have_timeout():
    for p in _py_files():
        for m in re.finditer(r"requests\.get\((.*?)\)", p.read_text(), re.DOTALL):
            assert "timeout=" in m.group(1), f"requests.get without timeout in {p}"
