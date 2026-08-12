/// Result of saving a PDF to a user-visible location.
class PdfSaveResult {
  const PdfSaveResult({
    this.path,
    this.uri,
    required this.displayPath,
    required this.filename,
    this.sharedViaSheet = false,
  });

  final String? path;
  final String? uri;
  final String displayPath;
  final String filename;
  final bool sharedViaSheet;

  bool get canOpen =>
      (uri != null && uri!.isNotEmpty) || (path != null && path!.isNotEmpty);
}

String buildDailyBookletFilename({
  required String examType,
  DateTime? date,
}) {
  final d = date ?? DateTime.now();
  final exam = examType
      .trim()
      .toUpperCase()
      .replaceAll(RegExp(r'[^A-Z0-9]+'), '_')
      .replaceAll(RegExp(r'_+'), '_')
      .replaceAll(RegExp(r'^_|_$'), '');
  final examPart = exam.isEmpty ? 'DENEME' : exam;
  final dd = d.day.toString().padLeft(2, '0');
  final mm = d.month.toString().padLeft(2, '0');
  return 'StudyOS_${examPart}_Gunluk_Deneme_$dd-$mm-${d.year}.pdf';
}

DateTime? parseChallengeDate(Object? raw) {
  if (raw == null) return null;
  if (raw is DateTime) return raw;
  final s = raw.toString().trim();
  if (s.isEmpty) return null;
  try {
    return DateTime.parse(s.length >= 10 ? s.substring(0, 10) : s);
  } catch (_) {
    return null;
  }
}

Future<String> savePdfBytes(List<int> bytes, String filename) async {
  throw UnsupportedError('PDF indirme bu platformda desteklenmiyor');
}

Future<PdfSaveResult> saveDailyBookletPdf({
  required List<int> bytes,
  required String examType,
  DateTime? challengeDate,
}) async {
  throw UnsupportedError('PDF indirme bu platformda desteklenmiyor');
}

Future<void> openSavedPdf(PdfSaveResult result) async {
  throw UnsupportedError('PDF açma bu platformda desteklenmiyor');
}
