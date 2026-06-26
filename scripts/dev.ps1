# Train Tools - 本地开发调试
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "=== Train Tools Dev ===" -ForegroundColor Cyan

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] npm not found. Install Node.js first." -ForegroundColor Red
    exit 1
}

# 1. 启动 Vite dev server (后台)
$vite = Start-Process -NoNewWindow -PassThru -FilePath "cmd.exe" -ArgumentList "/c npm.cmd run dev" -WorkingDirectory "$root\frontend"
Write-Host "[Vite] Dev server starting on http://localhost:5173" -ForegroundColor Green

# 等待 Vite 就绪（最多 15 秒）
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 1
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
}
if (-not $ready) {
    Write-Host "[WARN] Vite may not be ready yet, starting anyway..." -ForegroundColor Yellow
}

try {
    # 2. 启动桌面应用
    $env:ENV = "dev"
    Write-Host "[Desktop] Launching pywebview..." -ForegroundColor Yellow
    $result = uv run python -c "from backend.desktop import start_app; start_app()" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Desktop app exited with code $LASTEXITCODE" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
} finally {
    if (-not $vite.HasExited) { $vite.Kill() }
    Write-Host "=== Dev stopped ===" -ForegroundColor Cyan
}
