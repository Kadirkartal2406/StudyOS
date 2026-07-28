// StudyOS kök widget smoke testi.
//
// Not: Bu dosya, `flutter create` ile gelen varsayılan sayaç (counter) testinin
// yerine geçer. Eski test artık var olmayan `MyApp` sınıfını referans
// alıyordu ve gerçek uygulama yapısıyla (StudyOSApp, go_router, Riverpod)
// uyumsuzdu.

import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/app.dart';

void main() {
  // flutter_secure_storage platform kanalı widget testlerinde mock'lanmaz;
  // gerçek plugin implementasyonu olmadığı için istekler asla yanıtlanmaz ve
  // AuthNotifier.checkSession() sonsuza kadar askıda kalır. Boş oturum
  // (session yok) döndüren bir sahte handler tanımlayarak akışın
  // Unauthenticated durumuna doğal biçimde ilerlemesini sağlıyoruz.
  const secureStorageChannel = MethodChannel(
    'plugins.it_nomads.com/flutter_secure_storage',
  );

  TestWidgetsFlutterBinding.ensureInitialized();
  TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
      .setMockMethodCallHandler(secureStorageChannel, (call) async => null);

  testWidgets(
    'StudyOSApp splash ekranını gösterir ve oturum kontrolü sonrası '
    'giriş ekranına yönlendirir',
    (WidgetTester tester) async {
      await tester.pumpWidget(const ProviderScope(child: StudyOSApp()));

      // İlk karede splash ekranı görünür.
      expect(find.text('StudyOS'), findsOneWidget);

      // Splash ekranındaki CircularProgressIndicator süresiz döndüğü için
      // `pumpAndSettle` asla settle olmaz; bunun yerine sabit süreli `pump`
      // çağrıları ile animasyonun ve oturum kontrolü (checkSession) sonrası
      // router yönlendirmesinin tamamlanmasını bekliyoruz. Mock edilen
      // secure storage `null` döndürür (kayıtlı oturum yok), AuthNotifier
      // Unauthenticated durumuna geçer ve router guard login ekranına
      // yönlendirir.
      await tester.pump(const Duration(milliseconds: 1200));
      await tester.pump(const Duration(milliseconds: 500));

      expect(find.text('Hoş Geldin'), findsOneWidget);
    },
  );
}
