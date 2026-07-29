# StudyOS — Android Firebase App Distribution
#
# Usage:
#   .\scripts\distribute_android.ps1 `
#       -ApiBaseUrl "https://API_HOST/api/v1" `
#       [-FirebaseAppId "1:xxx:android:yyy"] `
#       [-Groups "beta"] `
#       [-SkipUpload]
#
# Prerequisites:
#   1) npm i -g firebase-tools
#   2) firebase login   (interactive, once)
#   3) Firebase Android app package: com.studyos.app

param(
    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,

    # Falls back to the mobilesdk_app_id from google-services.json
    [string]$FirebaseAppId = "",

    [string]$Groups = "beta",
    [string]$AppEnv = "beta",
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"
$root    = Split-Path -Parent $PSScriptRoot
$mobile  = Join-Path $root "mobile"

# ── Release Notes ────────────────────────────────────────────
$ReleaseNotes = @"
StudyOS Beta
• Daily Challenge düzeltmeleri
• Gemini soru üretimi iyileştirildi
• Question Pool geliştirmeleri
• Performans ve hata düzeltmeleri
"@

# ── API URL validation ────────────────────────────────────────
if ($ApiBaseUrl -notmatch '^https://') {
    Write-Warning "API_BASE_URL should be https:// for real devices. Got: $ApiBaseUrl"
}

# ── Auto-detect Firebase App ID ───────────────────────────────
if (-not $FirebaseAppId) {
    $gsJson = Join-Path $mobile "android\app\google-services.json"
    if (Test-Path $gsJson) {
        $gs = Get-Content $gsJson -Raw | ConvertFrom-Json
        $FirebaseAppId = $gs.client[0].client_info.mobilesdk_app_id
        Write-Host "==> Auto-detected Firebase App ID: $FirebaseAppId"
    } else {
        throw "FirebaseAppId not provided and google-services.json not found at: $gsJson"
    }
}

# ── Version info ──────────────────────────────────────────────
$pubspec = Join-Path $mobile "pubspec.yaml"
$versionLine = (Get-Content $pubspec | Where-Object { $_ -match '^version:' })
Write-Host ""
Write-Host "=============================================="
Write-Host "  StudyOS Beta Distribution"
Write-Host "  $versionLine"
Write-Host "  Groups : $Groups"
Write-Host "  App ID : $FirebaseAppId"
Write-Host "=============================================="
Write-Host ""

Push-Location $mobile
try {
    # ── Step 1: Clean ─────────────────────────────────────────
    Write-Host "[1/4] flutter clean..."
    flutter clean

    # ── Step 2: Get packages ──────────────────────────────────
    Write-Host "[2/4] flutter pub get..."
    flutter pub get

    # ── Step 3: Build APK ─────────────────────────────────────
    Write-Host "[3/4] flutter build apk --release..."
    flutter build apk --release `
        --dart-define="API_BASE_URL=$ApiBaseUrl" `
        --dart-define="APP_ENV=$AppEnv"

    # ── Step 4: Verify APK ────────────────────────────────────
    $apk = Join-Path $mobile "build\app\outputs\flutter-apk\app-release.apk"
    if (-not (Test-Path $apk)) {
        throw "APK not found at expected path: $apk"
    }
    $apkSizeMB = [math]::Round((Get-Item $apk).Length / 1MB, 2)
    Write-Host "[4/4] APK verified: $apk ($apkSizeMB MB)"

    if ($SkipUpload) {
        Write-Host ""
        Write-Host "SkipUpload set — skipping Firebase upload."
        Write-Host "Upload manually:"
        Write-Host "  firebase appdistribution:distribute '$apk' --app $FirebaseAppId --groups $Groups"
        return
    }

    # ── Step 5: Firebase CLI check ────────────────────────────
    $firebase = Get-Command firebase -ErrorAction SilentlyContinue
    if (-not $firebase) {
        Write-Host ""
        Write-Host "ERROR: firebase CLI not found." -ForegroundColor Red
        Write-Host "Install it and authenticate:"
        Write-Host "  npm i -g firebase-tools"
        Write-Host "  firebase login"
        throw "firebase CLI missing."
    }

    # ── Step 6: Upload to Firebase App Distribution ───────────
    Write-Host ""
    Write-Host "==> Uploading to Firebase App Distribution (group: $Groups)..."
    firebase appdistribution:distribute $apk `
        --app $FirebaseAppId `
        --groups $Groups `
        --release-notes $ReleaseNotes

    Write-Host ""
    Write-Host "=============================================="
    Write-Host "  Distribution SUCCESSFUL"
    Write-Host "  Beta users in group '$Groups' will receive"
    Write-Host "  an update notification shortly."
    Write-Host "=============================================="
}
finally {
    Pop-Location
}
