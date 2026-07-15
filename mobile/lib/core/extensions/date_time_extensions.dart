import 'package:intl/intl.dart';

/// Tarih ve zaman biçimlendirme yardımcıları.
extension DateTimeExtensions on DateTime {
  /// "15 Ocak 2025" formatı
  String get formattedDate => DateFormat('d MMMM yyyy', 'tr_TR').format(this);

  /// "15 Oca" formatı
  String get shortDate => DateFormat('d MMM', 'tr_TR').format(this);

  /// "14:30" formatı
  String get formattedTime => DateFormat('HH:mm').format(this);

  /// "15 Ocak 2025, 14:30" formatı
  String get formattedDateTime =>
      DateFormat('d MMMM yyyy, HH:mm', 'tr_TR').format(this);

  /// Bugün mü?
  bool get isToday {
    final now = DateTime.now();
    return year == now.year && month == now.month && day == now.day;
  }

  /// Dün mü?
  bool get isYesterday {
    final yesterday = DateTime.now().subtract(const Duration(days: 1));
    return year == yesterday.year &&
        month == yesterday.month &&
        day == yesterday.day;
  }

  /// Aynı gün mü?
  bool isSameDay(DateTime other) =>
      year == other.year && month == other.month && day == other.day;
}
