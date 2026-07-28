/// Saat/dakika değeri — domain katmanı Flutter framework'üne bağımlı olmasın
/// diye `TimeOfDay` yerine kullanılan saf Dart değer nesnesi.
class StudyTime {
  const StudyTime({required this.hour, required this.minute});

  final int hour;
  final int minute;

  /// Backend'den gelen "HH:MM:SS" formatını parse eder.
  static StudyTime? fromApi(String? value) {
    if (value == null || value.isEmpty) return null;
    final parts = value.split(':');
    return StudyTime(hour: int.parse(parts[0]), minute: int.parse(parts[1]));
  }

  /// Backend'e gönderilecek "HH:MM:SS" formatı.
  String toApi() =>
      '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}:00';

  /// Ekranda gösterilecek "HH:MM" formatı.
  String get label =>
      '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';

  int get totalMinutes => hour * 60 + minute;

  @override
  bool operator ==(Object other) =>
      other is StudyTime && other.hour == hour && other.minute == minute;

  @override
  int get hashCode => Object.hash(hour, minute);
}
