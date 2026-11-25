import json
import os
import subprocess
import sys
from pathlib import Path


def test_json_report_is_machine_readable(tmp_path: Path) -> None:
    (tmp_path / "hello.py").write_text("print(1)", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "claudescan", str(tmp_path), "--json"],
        check=True, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    report = json.loads(result.stdout)
    assert report["languages"][0]["name"] == "Python"
    assert list(tmp_path.iterdir()) == [tmp_path / "hello.py"]
