# Train Tools - 构建目录分发
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$venvPython = "$root\.venv\Scripts\python.exe"

$originalPath = $env:Path
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "=== Building Train Tools (Directory) ===" -ForegroundColor Cyan

try {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] npm not found. Install Node.js first." -ForegroundColor Red
        exit 1
    }

    if (-not (Test-Path $venvPython)) {
        Write-Host "[Setup] Creating venv and installing Python dependencies..." -ForegroundColor Yellow
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { python -m pip install uv 2>&1 | Out-Null }
        python -m uv sync
        if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }
    }

    Write-Host "[1/3] Building frontend..." -ForegroundColor Yellow
    Push-Location "$root\frontend"
    cmd.exe /c "npm install && npm run build"
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
    Pop-Location

    Write-Host "[2/3] Installing PyInstaller..." -ForegroundColor Yellow
    & $venvPython -m ensurepip --upgrade 2>&1 | Out-Null
    & $venvPython -m pip install pyinstaller 2>&1
    if ($LASTEXITCODE -ne 0) { throw "pip install pyinstaller failed" }

    Write-Host "[3/3] Packaging directory..." -ForegroundColor Yellow
    if (Test-Path "$root\dist") { cmd.exe /c "rmdir /s /q `"$root\dist`"" 2>&1 | Out-Null }
    if (Test-Path "$root\build") { Remove-Item -Recurse -Force "$root\build" -ErrorAction SilentlyContinue }
    Remove-Item -Force "$root\*.spec" -ErrorAction SilentlyContinue

    & $venvPython -m PyInstaller @(
        '--noconfirm', '--onedir', '--windowed',
        '--name', 'train-tools',
        "--add-data=$root\frontend\dist;frontend\dist",
        '--hidden-import', 'webview',
        '--hidden-import', 'uvicorn',
        '--hidden-import', 'fastapi',
        '--hidden-import', 'backend.main',
        "$root\main.py"
    )
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

    Write-Host "=== Build complete: dist\train-tools\ ===" -ForegroundColor Cyan
} finally {
    $env:Path = $originalPath
}
