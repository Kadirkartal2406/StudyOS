/// Tarih/saat ile ilgili yardımcı fonksiyonlar.
/// `intl` locale verisi başlatma gerekmeden çalışır (Türkçe sabit diziler).
class DateTimeHelper {
  DateTimeHelper._();

  static const _weekdays = [
    'Pazartesi',
    'Salı',
    'Çarşamba',
    'Perşembe',
    'Cuma',
    'Cumartesi',
    'Pazar',
  ];

  static const _months = [
    'Ocak',
    'Şubat',
    'Mart',
    'Nisan',
    'Mayıs',
    'Haziran',
    'Temmuz',
    'Ağustos',
    'Eylül',
    'Ekim',
    'Kasım',
    'Aralık',
  ];

  /// Saate göre karşılama mesajı üretir.
  /// 05:00–11:59 → Günaydın · 12:00–17:59 → İyi Günler · 18:00–04:59 → İyi Akşamlar
  static String greetingFor(DateTime now) {
    final hour = now.hour;
    if (hour >= 5 && hour < 12) return 'Günaydın';
    if (hour >= 12 && hour < 18) return 'İyi Günler';
    return 'İyi Akşamlar';
  }

  /// "15 Temmuz 2026, Çarşamba" formatında tam tarih döner.
  static String formatFullDate(DateTime date) {
    final weekday = _weekdays[date.weekday - 1];
    final month = _months[date.month - 1];
    return '${date.day} $month ${date.year}, $weekday';
  }
}
