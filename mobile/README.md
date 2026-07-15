# StudyOS Mobile

Flutter iOS + Android uygulaması.

## Kurulum

```bash
flutter pub get
flutter run
```

## Kod Üretimi (build_runner)

```bash
dart run build_runner build --delete-conflicting-outputs
```

## Test

```bash
flutter test
flutter test --coverage
```

## Linting

```bash
dart format lib/ test/
flutter analyze
```

## Yapı

```
lib/
├── main.dart            ← Giriş noktası
├── app.dart             ← MaterialApp.router
├── core/
│   ├── constants/       ← AppConfig, API URL
│   ├── errors/          ← AppException sınıfları
│   ├── extensions/      ← Dart extension metodları
│   ├── network/         ← Dio konfigürasyonu
│   ├── router/          ← GoRouter tanımı
│   ├── theme/           ← AppTheme, AppColors
│   └── utils/           ← Tarih, validasyon yardımcıları
├── features/
│   ├── auth/            ← Giriş, kayıt, şifre sıfırlama
│   ├── dashboard/       ← Ana sayfa
│   ├── study_plan/      ← Günlük plan (S-06)
│   ├── subject_tracker/ ← Konu takibi (S-08)
│   ├── pomodoro/        ← Zamanlayıcı (S-10)
│   ├── statistics/      ← İstatistikler (S-14)
│   ├── notifications/   ← Bildirimler (S-17)
│   ├── subscription/    ← Premium (S-19)
│   └── profile/         ← Profil (S-03)
├── shared/
│   ├── widgets/         ← AppButton, AppTextField, vb.
│   ├── models/          ← Paylaşımlı modeller
│   └── providers/       ← Paylaşımlı Riverpod provider'lar
└── services/            ← Platform servisleri (S3, FCM, Analytics)
```
