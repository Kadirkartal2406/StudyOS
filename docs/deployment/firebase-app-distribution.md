# Firebase App Distribution (Android)

StudyOS Android paket kimliği: `com.studyos.app`

## 1. Firebase projesi

1. [Firebase Console](https://console.firebase.google.com/) → proje oluştur (veya mevcut)
2. **Add app → Android**
3. Package name: `com.studyos.app`
4. `google-services.json` indir → `mobile/android/app/google-services.json`
5. App Distribution → tester grubu oluştur (örn. `testers`) + e-posta ekle
6. Android **App ID**’yi kopyala (`1:123…:android:abc…`)

## 2. CLI

```powershell
npm i -g firebase-tools
firebase login
```

## 3. Canlı API

App Distribution cihazları `localhost` göremez. Backend’i HTTPS ile yayınla, örn.:

`https://api.senin-domainin.com/api/v1`

## 4. Build + yükle

```powershell
.\scripts\distribute_android.ps1 `
  -ApiBaseUrl "https://api.senin-domainin.com/api/v1" `
  -FirebaseAppId "1:XXXX:android:YYYY" `
  -Groups "testers"
```

Sadece APK üretmek için: `-SkipUpload`

APK yolu: `mobile/build/app/outputs/flutter-apk/app-release.apk`

## 5. İmza (Play Store için sonra)

```powershell
keytool -genkey -v -keystore mobile/android/keystore/studyos-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias studyos
copy mobile\android\key.properties.example mobile\android\key.properties
# key.properties içini doldur
```

App Distribution ilk beta için debug imza kabul edilir.

## 6. iOS

Henüz `mobile/ios` yok — App Distribution iOS sonraki adım.
