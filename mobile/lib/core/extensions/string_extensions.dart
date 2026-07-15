/// Süre biçimlendirme yardımcıları.
extension DurationExtensions on Duration {
  /// "1 sa 25 dk" formatı
  String get formatted {
    final h = inHours;
    final m = inMinutes.remainder(60);
    if (h > 0) return '$h sa $m dk';
    return '$m dk';
  }

  /// "01:25:00" formatı (zamanlayıcı gösterimi)
  String get timerFormat {
    final h = inHours.toString().padLeft(2, '0');
    final m = inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = inSeconds.remainder(60).toString().padLeft(2, '0');
    if (inHours > 0) return '$h:$m:$s';
    return '$m:$s';
  }
}

/// String yardımcıları.
extension StringExtensions on String {
  /// İlk harfi büyüt
  String get capitalize =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';

  /// Geçerli e-posta adresi mi?
  bool get isValidEmail =>
      RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
          .hasMatch(this);

  /// Geçerli güçlü şifre mi? (min 8 karakter)
  bool get isValidPassword => length >= 8;
}
