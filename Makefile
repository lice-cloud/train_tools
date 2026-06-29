SHELL := powershell.exe

.PHONY: all desktop dev-backend dev-frontend
.PHONY: frontend pyinstaller clean-build build-exe build-dir-only
.PHONY: build build-dir clean

all: desktop

# ==================== Development ====================

desktop:
	@powershell -ExecutionPolicy Bypass -File scripts\dev.ps1

dev-backend:
	@$$env:ENV="dev"; uv run uvicorn backend.main:app --reload

dev-frontend:
	@cmd.exe /c "cd /d frontend && npm.cmd run dev"

# ==================== Build Steps ====================

frontend:
	cmd.exe /c "cd /d frontend && npm install && npm run build"

pyinstaller:
	.venv\Scripts\python.exe -m ensurepip --upgrade 2>&1 | Out-Null
	.venv\Scripts\python.exe -m pip install pyinstaller 2>&1

clean-build:
	cmd.exe /c "if exist dist rmdir /s /q dist"
	cmd.exe /c "if exist build rmdir /s /q build"
	cmd.exe /c "del /f /q *.spec 2>nul"

build-exe:
	python -m uv run pyinstaller --noconfirm --onefile --windowed --name train-tools --add-data "frontend\dist;frontend\dist" --hidden-import webview --hidden-import uvicorn --hidden-import fastapi --hidden-import backend.main main.py

build-dir-only:
	python -m uv run pyinstaller --noconfirm --onedir --windowed --name train-tools --add-data "frontend\dist;frontend\dist" --hidden-import webview --hidden-import uvicorn --hidden-import fastapi --hidden-import backend.main main.py

# ==================== Convenience ====================

build: frontend pyinstaller clean-build build-exe

build-dir: frontend pyinstaller clean-build build-dir-only

# ==================== Full Clean ====================

clean:
	cmd.exe /c "if exist frontend\node_modules rmdir /s /q frontend\node_modules"
	cmd.exe /c "if exist frontend\dist rmdir /s /q frontend\dist"
	cmd.exe /c "if exist .venv rmdir /s /q .venv"
	cmd.exe /c "if exist dist rmdir /s /q dist"
	cmd.exe /c "if exist build rmdir /s /q build"
	cmd.exe /c "del /f /q *.spec 2>nul"
	Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
