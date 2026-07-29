# StudyOS — Android Firebase App Distribution
#
# Usage:
#   .\scripts\distribute_android.ps1 -ApiBaseUrl "https://API_HOST/api/v1" -FirebaseAppId "1:xxx:android:yyy" -Groups "testers"
#
# Prerequisites:
#   1) npm i -g firebase-tools
#   2) firebase login   (interactive, once)
#   3) Firebase Android app package: com.studyos.app
#   4) Live HTTPS API (localhost will not work on phones)

param(
    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,

    [Parameter(Mandatory = $true)]
    [string]$FirebaseAppId,

    [string]$Groups = "testers",
    [string]$AppEnv = "beta",
    [string]$ReleaseNotes = "StudyOS beta - Firebase App Distribution",
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$mobile = Join-Path $root "mobile"

if ($ApiBaseUrl -notmatch '^https://') {
    Write-Warning "API_BASE_URL should be https:// for real devices. Got: $ApiBaseUrl"
}

Push-Location $mobile
try {
    Write-Host "==> flutter build apk --release"
    flutter build apk --release `
        --dart-define="API_BASE_URL=$ApiBaseUrl" `
        --dart-define="APP_ENV=$AppEnv"

    $apk = Join-Path $mobile "build\app\outputs\flutter-apk\app-release.apk"
    if (-not (Test-Path $apk)) {
        throw "APK not found: $apk"
    }
    Write-Host "APK ready: $apk"

    if ($SkipUpload) {
        Write-Host "SkipUpload set — upload manually with firebase appdistribution:distribute"
        return
    }

    $firebase = Get-Command firebase -ErrorAction SilentlyContinue
    if (-not $firebase) {
        throw "firebase CLI missing. Run: npm i -g firebase-tools && firebase login"
    }

    Write-Host "==> firebase appdistribution:distribute"
    firebase appdistribution:distribute $apk `
        --app $FirebaseAppId `
        --groups $Groups `
        --release-notes $ReleaseNotes
}
finally {
    Pop-Location
}
