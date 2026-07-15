#!/usr/bin/env pwsh
# StudyOS — Geliştirme Ortamı Kurulum Betiği
# Kullanım: .\scripts\setup.ps1
# Gereksinim: PowerShell 5.1+, Git, Docker Desktop

param(
    [switch]$SkipFlutter,
    [switch]$SkipDocker
)

Write-Host ""
Write-Host "╔═══════════════════════════════════╗"
Write-Host "║   StudyOS Kurulum Betiği           ║"
Write-Host "╚═══════════════════════════════════╝"
Write-Host ""

$ROOT = Split-Path -Parent $PSScriptRoot
$BACKEND = "$ROOT\backend"
$MOBILE = "$ROOT\mobile"
$WEB = "$ROOT\web"

# ── 1. .env kontrolü ─────────────────────────────────────────
Write-Host "[1/5] Ortam değişkenleri kontrol ediliyor..."
if (!(Test-Path "$ROOT\.env")) {
    Copy-Item "$ROOT\.env.example" "$ROOT\.env"
    Write-Host "  ✓ .env.example'dan .env oluşturuldu. Lütfen değerleri düzenleyin."
} else {
    Write-Host "  ✓ .env mevcut"
}

# ── 2. Backend bağımlılıkları ─────────────────────────────────
Write-Host ""
Write-Host "[2/5] Backend bağımlılıkları yükleniyor..."
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "  uv bulunamadı, pip ile kuruluyor..."
    pip install uv --quiet
}
Push-Location $BACKEND
uv sync --extra dev
Write-Host "  ✓ Backend bağımlılıkları hazır"
Pop-Location

# ── 3. Flutter bağımlılıkları ────────────────────────────────
if (!$SkipFlutter) {
    Write-Host ""
    Write-Host "[3/5] Flutter bağımlılıkları yükleniyor..."
    $flutter = if (Test-Path "C:\flutter\bin\flutter.exe") { "C:\flutter\bin\flutter.exe" } else { "flutter" }

    if (Get-Command $flutter -ErrorAction SilentlyContinue) {
        Push-Location $MOBILE
        & $flutter pub get
        Write-Host "  ✓ Mobile bağımlılıkları hazır"
        Pop-Location

        Push-Location $WEB
        & $flutter pub get
        Write-Host "  ✓ Web bağımlılıkları hazır"
        Pop-Location
    } else {
        Write-Host "  ⚠ Flutter bulunamadı. https://flutter.dev/docs/get-started adresinden kurun."
    }
} else {
    Write-Host ""
    Write-Host "[3/5] Flutter adımı atlandı (--SkipFlutter)"
}

# ── 4. Docker servisleri ──────────────────────────────────────
if (!$SkipDocker) {
    Write-Host ""
    Write-Host "[4/5] Docker servisleri başlatılıyor..."
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Push-Location $ROOT
        docker compose up -d postgres minio
        Write-Host "  ✓ PostgreSQL ve MinIO başlatıldı"
        Pop-Location
    } else {
        Write-Host "  ⚠ Docker bulunamadı. Docker Desktop kurun veya --SkipDocker kullanın."
    }
} else {
    Write-Host ""
    Write-Host "[4/5] Docker adımı atlandı (--SkipDocker)"
}

# ── 5. Ortam değişkeni doğrulama ─────────────────────────────
Write-Host ""
Write-Host "[5/5] Ortam değişkenleri doğrulanıyor..."
Push-Location $ROOT
python scripts/check_env.py
Pop-Location

Write-Host ""
Write-Host "╔═══════════════════════════════════╗"
Write-Host "║   Kurulum tamamlandı!              ║"
Write-Host "╚═══════════════════════════════════╝"
Write-Host ""
Write-Host "Backend başlatmak için:"
Write-Host "  cd backend && uv run uvicorn app.main:app --reload"
Write-Host ""
Write-Host "API Docs: http://localhost:8000/api/docs"
Write-Host ""
