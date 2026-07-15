# StudyOS Web — Kurumsal Panel

Flutter Web uygulaması — dershane ve eğitim kurumları yönetim paneli.

## Kurulum

```bash
flutter pub get
flutter run -d chrome
```

## Production Build

```bash
flutter build web --release
```

## Test & Lint

```bash
flutter test
dart format lib/ test/
flutter analyze
```

## Yapı

```
lib/
├── main.dart              ← Giriş noktası
├── app.dart               ← MaterialApp.router
├── core/
│   ├── constants/
│   ├── router/            ← GoRouter (web routing)
│   └── theme/             ← WebAppTheme
├── features/
│   ├── auth/              ← Kurum girişi
│   ├── dashboard/         ← Genel bakış
│   ├── students/          ← Öğrenci yönetimi (K-04)
│   ├── classes/           ← Sınıf yönetimi (K-03)
│   ├── exams/             ← Sınav yönetimi (K-14)
│   └── reports/           ← Raporlar (K-15)
└── shared/widgets/
```
