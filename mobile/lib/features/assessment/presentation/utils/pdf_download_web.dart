import 'dart:html' as html;
import 'dart:typed_data';

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

  bool get canOpen => false;
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
  final result = await saveDailyBookletPdf(
    bytes: bytes,
    examType: 'WEB',
    challengeDate: DateTime.now(),
  );
  return result.filename;
}

Future<PdfSaveResult> saveDailyBookletPdf({
  required List<int> bytes,
  required String examType,
  DateTime? challengeDate,
}) async {
  final filename = buildDailyBookletFilename(
    examType: examType,
    date: challengeDate,
  );
  final data = Uint8List.fromList(bytes);
  final blob = html.Blob([data], 'application/pdf');
  final url = html.Url.createObjectUrlFromBlob(blob);
  html.AnchorElement(href: url)
    ..setAttribute('download', filename)
    ..click();
  html.Url.revokeObjectUrl(url);
  return PdfSaveResult(
    displayPath: filename,
    filename: filename,
  );
}

Future<void> openSavedPdf(PdfSaveResult result) async {
  // Browser download already triggered; nothing to open in-app.
}
