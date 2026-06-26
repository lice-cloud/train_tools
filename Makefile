SHELL := powershell.exe

.PHONY: all desktop build dev-backend dev-frontend clean

all: desktop

desktop:
	@powershell -ExecutionPolicy Bypass -File scripts\dev.ps1

build:
	@powershell -ExecutionPolicy Bypass -File scripts\build.ps1

dev-backend:
	@$$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User"); $$env:ENV="dev"; uv run uvicorn backend.main:app --reload

dev-frontend:
	@$$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User"); cmd.exe /c "cd /d frontend && npm.cmd run dev"

clean:
	@$$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User"); if (Test-Path frontend\node_modules) { Remove-Item -Recurse -Force frontend\node_modules }; if (Test-Path frontend\dist) { Remove-Item -Recurse -Force frontend\dist }; if (Test-Path build) { Remove-Item -Recurse -Force build }; if (Test-Path dist) { Remove-Item -Recurse -Force dist }; Remove-Item -Force *.spec -ErrorAction SilentlyContinue; Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
