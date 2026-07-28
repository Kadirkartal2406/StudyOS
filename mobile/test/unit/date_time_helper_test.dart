import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/core/utils/date_time_helper.dart';

void main() {
  group('DateTimeHelper.greetingFor', () {
    test('sabah saatlerinde Günaydın döner', () {
      final morning = DateTime(2026, 7, 15, 8);
      expect(DateTimeHelper.greetingFor(morning), 'Günaydın');
    });

    test('öğlen ve öğleden sonra İyi Günler döner', () {
      final afternoon = DateTime(2026, 7, 15, 14);
      expect(DateTimeHelper.greetingFor(afternoon), 'İyi Günler');
    });

    test('akşam ve gece İyi Akşamlar döner', () {
      final evening = DateTime(2026, 7, 15, 21);
      final night = DateTime(2026, 7, 15, 2);
      expect(DateTimeHelper.greetingFor(evening), 'İyi Akşamlar');
      expect(DateTimeHelper.greetingFor(night), 'İyi Akşamlar');
    });

    test('sınır saatler doğru dilime düşer', () {
      expect(DateTimeHelper.greetingFor(DateTime(2026, 7, 15, 5)), 'Günaydın');
      expect(DateTimeHelper.greetingFor(DateTime(2026, 7, 15, 12)), 'İyi Günler');
      expect(DateTimeHelper.greetingFor(DateTime(2026, 7, 15, 18)), 'İyi Akşamlar');
    });
  });

  group('DateTimeHelper.formatFullDate', () {
    test('Türkçe gün ve ay adlarıyla tam tarih döner', () {
      final date = DateTime(2026, 7, 15); // Çarşamba
      expect(DateTimeHelper.formatFullDate(date), '15 Temmuz 2026, Çarşamba');
    });

    test('yıl başındaki bir tarihi doğru formatlar', () {
      final date = DateTime(2026, 1, 1); // Perşembe
      expect(DateTimeHelper.formatFullDate(date), '1 Ocak 2026, Perşembe');
    });
  });
}
