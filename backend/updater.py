import os
import sys
import json
import struct
import urllib.request
import urllib.error
import tempfile
import subprocess
import re
import time
import tomllib
import threading
from pathlib import Path

GITHUB_REPO = "lice-cloud/train_tools"

CURRENT_VERSION = "1.0.3"

_download_state: dict = {}


def _get_current_version() -> str:
    if getattr(sys, "frozen", False):
        return CURRENT_VERSION
    try:
        p = Path(__file__).resolve().parent.parent / "pyproject.toml"
        with open(p, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return CURRENT_VERSION


def _parse_version(s: str) -> tuple:
    parts = s.split(".")
    nums = []
    pre = False
    for p in parts:
        m = re.match(r"(\d+)(.*)", p)
        if m:
            nums.append(int(m.group(1)))
            suffix = m.group(2).strip("-")
            if suffix:
                pre = True
                nums.append(suffix)
        else:
            nums.append(0)
    return (pre, nums)


def _compare_versions(a: str, b: str) -> int:
    pre_a, nums_a = _parse_version(a)
    pre_b, nums_b = _parse_version(b)
    max_l = max(len(nums_a), len(nums_b))
    nums_a += [0] * (max_l - len(nums_a))
    nums_b += [0] * (max_l - len(nums_b))
    for x, y in zip(nums_a, nums_b):
        if isinstance(x, str) and isinstance(y, str):
            if x > y:
                return 1
            if x < y:
                return -1
        elif isinstance(x, str):
            return -1
        elif isinstance(y, str):
            return 1
        elif x > y:
            return 1
        elif x < y:
            return -1
    if pre_a and not pre_b:
        return -1
    if not pre_a and pre_b:
        return 1
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
        asset_info = {}
        for asset in data.get("assets", []):
            if asset.get("name") == "train-tools.exe":
                asset_info = {
                    "download_url": asset.get("browser_download_url", ""),
                    "size": asset.get("size", 0),
                }
                break

        return {
            "has_update": _compare_versions(latest_tag, current) > 0,
            "current_version": current,
            "latest_version": latest_tag,
            "asset_size": asset_info.get("size", 0),
            "download_url": asset_info.get("download_url", ""),
            "release_notes": data.get("body", ""),
        }
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        return {"has_update": False, "current_version": current, "error": str(e)}


def _is_valid_exe(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            if f.read(2) != b"MZ":
                return False
            f.seek(0x3C)
            pe_offset = struct.unpack("<I", f.read(4))[0]
            f.seek(pe_offset)
            if f.read(4) != b"PE\x00\x00":
                return False
            return True
    except Exception:
        return False


def _progress_hook(block: int, block_size: int, total_size: int):
    state = _download_state.get("_int")
    if state is None:
        return
    if total_size > 0:
        pct = min(int(block * block_size * 100 / total_size), 100)
        state["progress"] = pct


def _download_worker(url: str, expected_size: int):
    state = {"status": "downloading", "progress": 0, "int": None}
    _download_state["_int"] = state
    dest = os.path.join(tempfile.gettempdir(), "train-tools-new.exe")
    last_error = ""
    for attempt in range(3):
        if attempt > 0:
            time.sleep(1)
        try:
            urllib.request.urlretrieve(url, dest, _progress_hook)
            actual = os.path.getsize(dest)
            if expected_size > 0 and actual != expected_size:
                raise IOError(f"size mismatch: expected {expected_size}, got {actual}")
            if not _is_valid_exe(dest):
                raise IOError("downloaded file is not a valid PE executable")
            state["status"] = "ready"
            state["dest"] = dest
            _download_state["status"] = "ready"
            _download_state["dest"] = dest
            _download_state["progress"] = 100
            return
        except Exception as e:
            last_error = str(e)
            continue
    state["status"] = "error"
    state["error"] = last_error
    _download_state["status"] = "error"
    _download_state["error"] = last_error


def start_download(url: str, expected_size: int = 0):
    thread = threading.Thread(
        target=_download_worker, args=(url, expected_size), daemon=True
    )
    thread.start()


def get_download_status() -> dict:
    s = _download_state.get("_int", {})
    return {
        "status": s.get("status", "idle"),
        "progress": s.get("progress", 0),
        "error": s.get("error", ""),
    }


def apply_update() -> None:
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Update only works in frozen build")
    state = _download_state.get("_int", {})
    new_exe = state.get("dest", "")
    if not new_exe or not os.path.exists(new_exe):
        raise RuntimeError("No downloaded update found")
    current_exe = os.path.abspath(sys.argv[0])
    script = os.path.join(tempfile.gettempdir(), "update-train-tools.bat")
    pid = os.getpid()
    with open(script, "w") as f:
        f.write(f"""@echo off
:wait
tasklist /fi "PID eq {pid}" 2>nul | findstr "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait
)
copy /y "{new_exe}" "{current_exe}" >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    copy /y "{new_exe}" "{current_exe}" >nul 2>&1
)
if errorlevel 1 exit /b 1
del "{new_exe}" >nul 2>&1
start "" /b "{current_exe}"
""")
    subprocess.Popen(["cmd", "/c", script], close_fds=True)
    time.sleep(0.5)
    os._exit(0)
