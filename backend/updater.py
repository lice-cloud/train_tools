import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
import re
import tomllib
import threading
from pathlib import Path

GITHUB_REPO = "lice-cloud/train_tools"

CURRENT_VERSION = "1.0.1"

_download_state = {"status": "idle", "progress": 0, "dest": ""}


def _get_current_version() -> str:
    if getattr(sys, "frozen", False):
        return CURRENT_VERSION
    try:
        p = Path(__file__).resolve().parent.parent / "pyproject.toml"
        with open(p, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return CURRENT_VERSION


def _parse_version(s: str) -> list:
    parts = s.split(".")
    result = []
    for p in parts:
        m = re.match(r"(\d+)", p)
        result.append(int(m.group(1)) if m else 0)
    return result


def _compare_versions(a: str, b: str) -> int:
    pa = _parse_version(a)
    pb = _parse_version(b)
    max_l = max(len(pa), len(pb))
    pa += [0] * (max_l - len(pa))
    pb += [0] * (max_l - len(pb))
    for x, y in zip(pa, pb):
        if x > y:
            return 1
        if x < y:
            return -1
    return 0


def _auth_headers() -> dict:
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def check_update() -> dict:
    current = _get_current_version()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers=_auth_headers())
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


def _progress_hook(block: int, block_size: int, total_size: int):
    if total_size > 0:
        pct = min(int(block * block_size * 100 / total_size), 100)
        _download_state["progress"] = pct


def _download_worker(url: str):
    global _download_state
    _download_state["status"] = "downloading"
    _download_state["progress"] = 0
    dest = os.path.join(tempfile.gettempdir(), "train-tools-new.exe")
    try:
        urllib.request.urlretrieve(url, dest, _progress_hook)
        _download_state["status"] = "ready"
        _download_state["dest"] = dest
    except Exception as e:
        _download_state["status"] = "error"
        _download_state["error"] = str(e)


def start_download(url: str):
    thread = threading.Thread(target=_download_worker, args=(url,), daemon=True)
    thread.start()


def get_download_status() -> dict:
    return {k: _download_state.get(k) for k in ("status", "progress", "error")}


def apply_update() -> None:
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Update only works in frozen build")
    new_exe = _download_state.get("dest", "")
    if not new_exe or not os.path.exists(new_exe):
        raise RuntimeError("No downloaded update found")
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
