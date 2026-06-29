SHELL := powershell.exe

.PHONY: all desktop dev-backend dev-frontend
.PHONY: frontend clean-build build build-dir clean

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

clean-build:
	cmd.exe /c "if exist dist rmdir /s /q dist"
	cmd.exe /c "if exist build rmdir /s /q build"
	cmd.exe /c "del /f /q *.spec 2>nul"

build:
	@powershell -ExecutionPolicy Bypass -File scripts\build.ps1

build-dir:
	@powershell -ExecutionPolicy Bypass -File scripts\build-dir.ps1

# ==================== Full Clean ====================

clean:
	cmd.exe /c "if exist frontend\node_modules rmdir /s /q frontend\node_modules"
	cmd.exe /c "if exist frontend\dist rmdir /s /q frontend\dist"
	cmd.exe /c "if exist .venv rmdir /s /q .venv"
	cmd.exe /c "if exist dist rmdir /s /q dist"
	cmd.exe /c "if exist build rmdir /s /q build"
	cmd.exe /c "del /f /q *.spec 2>nul"
	Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
