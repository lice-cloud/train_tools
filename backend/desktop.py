import threading
import os

import webview

from backend.main import app
import uvicorn


def start_app():
    port = 8000
    host = "http://localhost:5173" if os.environ.get("ENV") == "dev" else f"http://localhost:{port}"

    t = threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "127.0.0.1", "port": port, "log_level": "info"},
        daemon=True,
    )
    t.start()

    webview.create_window("Train Tools", host, width=1200, height=800)
    webview.start()


if __name__ == "__main__":
    start_app()
