// Meeting-010 — Gerçek backend'e karşı Flutter Authentication E2E testleri.
//
// Bu test dosyası mock kullanmaz: gerçek Dio istemcisi, gerçek
// flutter_secure_storage ve `http://localhost:8000` üzerinde çalışan gerçek
// backend'e karşı çalışır. Çalıştırmadan önce backend'in ayakta olması
// gerekir (bkz. docs/sprints/Sprint-1.2B-Integration.md).
//
// Çalıştırma:
//   flutter test integration_test/auth_flow_test.dart -d windows

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

import 'package:studyos_mobile/app.dart';
import 'package:studyos_mobile/core/router/app_router.dart';
import 'package:studyos_mobile/features/auth/presentation/providers/auth_provider.dart';
import 'package:studyos_mobile/features/auth/presentation/providers/auth_state.dart';

/// Splash ekranındaki sonsuz döngülü `CircularProgressIndicator` yüzünden
/// `pumpAndSettle` asla settle olmaz; bu yardımcı, gerçek zamanlı (integration
/// test) ortamda belirli bir koşul gerçekleşene kadar sınırlı sürede `pump`
/// çağırır.
Future<void> pumpUntil(
  WidgetTester tester,
  bool Function() condition, {
  Duration timeout = const Duration(seconds: 15),
  Duration step = const Duration(milliseconds: 200),
}) async {
  final deadline = DateTime.now().add(timeout);
  while (!condition() && DateTime.now().isBefore(deadline)) {
    await tester.pump(step);
  }
}

Future<void> clearSecureStorage() async {
  const storage = FlutterSecureStorage();
  await storage.deleteAll();
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUp(clearSecureStorage);
  tearDown(clearSecureStorage);

  testWidgets('Oturum yokken splash ekranı login ekranına yönlendirir', (
    tester,
  ) async {
    await tester.pumpWidget(const ProviderScope(child: StudyOSApp()));
    expect(find.text('StudyOS'), findsOneWidget);

    await pumpUntil(tester, () => find.text('Hoş Geldin').evaluate().isNotEmpty);

    expect(find.text('Hoş Geldin'), findsOneWidget);
  });

  testWidgets(
    'Kayıt ol -> giriş yap -> ana ekran -> çıkış yap (gerçek backend)',
    (tester) async {
      final email =
          'e2e.${DateTime.now().microsecondsSinceEpoch}@mailinator.com';
      const password = 'GucluSifre123';

      await tester.pumpWidget(const ProviderScope(child: StudyOSApp()));
      await pumpUntil(tester, () => find.text('Hoş Geldin').evaluate().isNotEmpty);

      // ── Kayıt Ol ekranına geç ──────────────────────────────
      await tester.tap(find.text('Kayıt Ol'));
      await tester.pumpAndSettle();

      final fields = find.byType(TextFormField);
      expect(fields, findsNWidgets(5));
      await tester.enterText(fields.at(0), 'Test');
      await tester.enterText(fields.at(1), 'Kullanıcı');
      await tester.enterText(fields.at(2), email);
      await tester.enterText(fields.at(3), password);
      await tester.enterText(fields.at(4), password);
      await tester.pump();

      await tester.tap(find.widgetWithText(FilledButton, 'Kayıt Ol'));

      // Register -> backend isteği tamamlanana ve login ekranına
      // yönlendirilene kadar bekle.
      await pumpUntil(
        tester,
        () => find.text('Kayıt başarılı! Giriş yapabilirsiniz.').evaluate().isNotEmpty,
      );
      expect(
        find.text('Kayıt başarılı! Giriş yapabilirsiniz.'),
        findsOneWidget,
      );

      await pumpUntil(tester, () => find.text('Hoş Geldin').evaluate().isNotEmpty);
      expect(find.text('Hoş Geldin'), findsOneWidget);

      // ── Giriş Yap ───────────────────────────────────────────
      final loginFields = find.byType(TextFormField);
      expect(loginFields, findsNWidgets(2));
      await tester.enterText(loginFields.at(0), email);
      await tester.enterText(loginFields.at(1), password);
      await tester.pump();
      await tester.tap(find.widgetWithText(FilledButton, 'Giriş Yap'));

      // Giriş sonrası Dashboard ekranı yüklenir (backend'den /dashboard verisi gelir).
      await pumpUntil(tester, () => find.text('Bugünkü Hedef').evaluate().isNotEmpty);
      expect(find.text('Bugünkü Hedef'), findsOneWidget);
      expect(find.textContaining('Test'), findsOneWidget);

      // ── Çıkış Yap ───────────────────────────────────────────
      await tester.tap(find.byIcon(Icons.logout_rounded));
      await pumpUntil(tester, () => find.text('Hoş Geldin').evaluate().isNotEmpty);
      expect(find.text('Hoş Geldin'), findsOneWidget);

      // Secure storage logout sonrası temizlenmiş olmalı.
      const storage = FlutterSecureStorage();
      final refreshToken = await storage.read(key: 'studyos_refresh_token');
      final user = await storage.read(key: 'studyos_current_user');
      expect(refreshToken, isNull);
      expect(user, isNull);
    },
  );

  testWidgets(
    'Yanlış şifre ile giriş, backend hata mesajını snackbar\'da gösterir',
    (tester) async {
      final email =
          'wrongpw.${DateTime.now().microsecondsSinceEpoch}@mailinator.com';
      const password = 'GucluSifre123';

      await tester.pumpWidget(const ProviderScope(child: StudyOSApp()));
      await pumpUntil(tester, () => find.text('Hoş Geldin').evaluate().isNotEmpty);

      // Önce gerçek bir kullanıcı oluştur (register akışı üzerinden).
      await tester.tap(find.text('Kayıt Ol'));
      await tester.pumpAndSettle();
      final regFields = find.byType(TextFormField);
      await tester.enterText(regFields.at(0), 'Test');
      await tester.enterText(regFields.at(1), 'Kullanıcı');
      await tester.enterText(regFields.at(2), email);
      await tester.enterText(regFields.at(3), password);
      await tester.enterText(regFields.at(4), password);
      await tester.pump();
      await tester.tap(find.widgetWithText(FilledButton, 'Kayıt Ol'));
      await pumpUntil(tester, () => find.text('Hoş Geldin').evaluate().isNotEmpty);

      // Yanlış şifre ile giriş dene.
      final loginFields = find.byType(TextFormField);
      await tester.enterText(loginFields.at(0), email);
      await tester.enterText(loginFields.at(1), 'TamamenYanlisSifre1');
      await tester.pump();
      await tester.tap(find.widgetWithText(FilledButton, 'Giriş Yap'));

      await pumpUntil(
        tester,
        () => find.text('E-posta veya şifre hatalı').evaluate().isNotEmpty,
      );
      expect(find.text('E-posta veya şifre hatalı'), findsOneWidget);
    },
  );

  testWidgets(
    'Auth guard: oturum yokken /dashboard rotasına gidilemez, /login\'e yönlendirilir',
    (tester) async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Guard'ın çalışması için Unauthenticated durumunu garanti et.
      container.read(authProvider.notifier).state = const AuthUnauthenticated();
      final router = container.read(appRouterProvider);

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: MaterialApp.router(routerConfig: router),
        ),
      );
      await tester.pumpAndSettle();

      router.go('/dashboard');
      await tester.pumpAndSettle();

      expect(find.text('Hoş Geldin'), findsOneWidget);
      expect(find.text('Bugünkü Hedef'), findsNothing);
    },
  );
}
