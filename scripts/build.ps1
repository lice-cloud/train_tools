# Train Tools - 构建单文件 exe
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "=== Building Train Tools ===" -ForegroundColor Cyan

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] npm not found. Install Node.js first." -ForegroundColor Red
    exit 1
}

# 1. 构建前端
Write-Host "[1/4] Building frontend..." -ForegroundColor Yellow
Push-Location "$root\frontend"
cmd.exe /c "npm.cmd install && npm.cmd run build"
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
Pop-Location

# 2. 安装构建依赖
Write-Host "[2/4] Installing build dependencies..." -ForegroundColor Yellow
uv pip install pyinstaller

# 3. 清理旧构建
Write-Host "[3/4] Cleaning old builds..." -ForegroundColor Yellow
if (Test-Path "$root\dist") { Remove-Item -Recurse -Force "$root\dist" }
if (Test-Path "$root\build") { Remove-Item -Recurse -Force "$root\build" }
Remove-Item -Force "$root\*.spec" -ErrorAction SilentlyContinue

# 4. 打包单文件 exe
Write-Host "[4/4] Packaging executable..." -ForegroundColor Yellow
uv run pyinstaller --noconfirm --onefile --windowed `
    --name "train-tools" `
    --add-data "$root\frontend\dist;frontend\dist" `
    --hidden-import pywebview `
    --hidden-import uvicorn `
    --hidden-import fastapi `
    --hidden-import backend.main `
    "$root\main.py"

Write-Host "=== Build complete: dist\train-tools.exe ===" -ForegroundColor Cyan
