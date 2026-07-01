import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
import tomllib
from pathlib import Path

GITHUB_REPO = "lice-cloud/train_tools"

CURRENT_VERSION = "1.0.0"


def _get_current_version() -> str:
    if getattr(sys, "frozen", False):
        return CURRENT_VERSION
    try:
        p = Path(__file__).resolve().parent.parent / "pyproject.toml"
        with open(p, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return CURRENT_VERSION


def _compare_versions(a: str, b: str) -> int:
    pa = [int(x) for x in a.split(".")]
    pb = [int(x) for x in b.split(".")]
    max_l = max(len(pa), len(pb))
    pa += [0] * (max_l - len(pa))
    pb += [0] * (max_l - len(pb))
    for x, y in zip(pa, pb):
        if x > y:
            return 1
        if x < y:
            return -1
    return 0


def check_update() -> dict:
    current = _get_current_version()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        latest_tag = data.get("tag_name", "").lstrip("v")
        download_url = ""
        for asset in data.get("assets", []):
            if asset.get("name") == "train-tools.exe":
                download_url = asset.get("browser_download_url", "")
                break

        return {
            "has_update": _compare_versions(latest_tag, current) > 0,
            "current_version": current,
            "latest_version": latest_tag,
            "download_url": download_url,
            "release_notes": data.get("body", ""),
        }
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        return {"has_update": False, "current_version": current, "error": str(e)}


def download_update(url: str) -> str:
    dest = os.path.join(tempfile.gettempdir(), "train-tools-new.exe")
    urllib.request.urlretrieve(url, dest)
    return dest


def apply_update(new_exe: str) -> None:
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Update only works in frozen build")
    current_exe = os.path.abspath(sys.argv[0])
    script = os.path.join(tempfile.gettempdir(), "update-train-tools.bat")
    with open(script, "w") as f:
        f.write(f"""@echo off
:wait
tasklist /fi "PID eq {os.getpid()}" 2>nul | findstr "{os.getpid()}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait
)
copy /y "{new_exe}" "{current_exe}" >nul 2>&1
del "{new_exe}"
start "" "{current_exe}"
""")
    subprocess.Popen(["cmd", "/c", script], shell=True)
    os._exit(0)
