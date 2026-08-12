import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:share_plus/share_plus.dart';

const _channel = MethodChannel('studyos/pdf_storage');

const kDailyBookletRelativePath = 'Download/StudyOS/Günlük Denemeler';
const kReportsRelativePath = 'Download/StudyOS/Raporlar';

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

/// StudyOS_TYT_Gunluk_Deneme_12-08-2026.pdf
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
  final yyyy = '${d.year}';
  return 'StudyOS_${examPart}_Gunluk_Deneme_$dd-$mm-$yyyy.pdf';
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

/// Backward-compatible save used by report PDF and generic callers.
Future<String> savePdfBytes(List<int> bytes, String filename) async {
  final result = await savePdfToUserVisibleLocation(
    bytes: bytes,
    filename: filename,
    relativePath: kReportsRelativePath,
  );
  return result.path ?? result.uri ?? result.displayPath;
}

Future<PdfSaveResult> saveDailyBookletPdf({
  required List<int> bytes,
  required String examType,
  DateTime? challengeDate,
}) {
  final filename = buildDailyBookletFilename(
    examType: examType,
    date: challengeDate,
  );
  return savePdfToUserVisibleLocation(
    bytes: bytes,
    filename: filename,
    relativePath: kDailyBookletRelativePath,
    preferShareSheetOnIos: true,
  );
}

Future<PdfSaveResult> savePdfToUserVisibleLocation({
  required List<int> bytes,
  required String filename,
  required String relativePath,
  bool preferShareSheetOnIos = false,
}) async {
  final safeName = _sanitizeFilename(filename);
  final data = Uint8List.fromList(bytes);

  if (Platform.isAndroid) {
    await _ensureLegacyWritePermission();
    try {
      final raw = await _channel.invokeMethod<Map<dynamic, dynamic>>(
        'savePdfToDownloads',
        <String, dynamic>{
          'bytes': data,
          'filename': safeName,
          'relativePath': relativePath,
        },
      );
      if (raw == null) {
        throw StateError('Android PDF kaydı boş döndü');
      }
      return PdfSaveResult(
        path: raw['path'] as String?,
        uri: raw['uri'] as String?,
        displayPath: (raw['displayPath'] as String?) ??
            '$relativePath/${raw['filename'] ?? safeName}',
        filename: (raw['filename'] as String?) ?? safeName,
      );
    } on PlatformException catch (e) {
      throw StateError(e.message ?? 'PDF kaydedilemedi');
    }
  }

  if (Platform.isIOS) {
    final dir = await getApplicationDocumentsDirectory();
    final folder = Directory('${dir.path}/StudyOS/Gunluk_Denemeler');
    if (!await folder.exists()) {
      await folder.create(recursive: true);
    }
    final unique = await _uniqueFile(folder, safeName);
    await unique.writeAsBytes(data, flush: true);
    if (preferShareSheetOnIos) {
      await SharePlus.instance.share(
        ShareParams(
          files: [XFile(unique.path, mimeType: 'application/pdf')],
          subject: safeName,
          text: 'StudyOS günlük deneme PDF',
        ),
      );
      return PdfSaveResult(
        path: unique.path,
        displayPath: 'Dosyalar / Paylaş',
        filename: unique.uri.pathSegments.isNotEmpty
            ? unique.uri.pathSegments.last
            : safeName,
        sharedViaSheet: true,
      );
    }
    return PdfSaveResult(
      path: unique.path,
      displayPath: unique.path,
      filename: unique.uri.pathSegments.isNotEmpty
          ? unique.uri.pathSegments.last
          : safeName,
    );
  }

  // Desktop / other: Downloads or Documents
  Directory? target;
  try {
    target = await getDownloadsDirectory();
  } catch (_) {
    target = null;
  }
  target ??= await getApplicationDocumentsDirectory();
  final folder = Directory('${target.path}/StudyOS/Günlük Denemeler');
  if (!await folder.exists()) {
    await folder.create(recursive: true);
  }
  final unique = await _uniqueFile(folder, safeName);
  await unique.writeAsBytes(data, flush: true);
  return PdfSaveResult(
    path: unique.path,
    displayPath: unique.path,
    filename: unique.uri.pathSegments.isNotEmpty
        ? unique.uri.pathSegments.last
        : safeName,
  );
}

Future<void> openSavedPdf(PdfSaveResult result) async {
  if (Platform.isAndroid) {
    try {
      await _channel.invokeMethod<void>('openPdf', <String, dynamic>{
        'uri': result.uri,
        'path': result.path,
      });
      return;
    } catch (_) {
      // Fall through to share sheet
    }
  }
  final path = result.path;
  if (path == null || path.isEmpty) {
    throw StateError('Açılacak PDF yolu bulunamadı');
  }
  await SharePlus.instance.share(
    ShareParams(
      files: [XFile(path, mimeType: 'application/pdf')],
      subject: result.filename,
    ),
  );
}

Future<void> _ensureLegacyWritePermission() async {
  if (!Platform.isAndroid) return;
  // MediaStore path (API 29+) needs no storage permission.
  // Legacy public Downloads write needs WRITE_EXTERNAL_STORAGE on API ≤ 28.
  if (defaultTargetPlatform != TargetPlatform.android) return;
  try {
    final status = await Permission.storage.status;
    if (status.isGranted || status.isLimited) return;
    // On modern Android this permission is no-op / denied; ignore failures.
    await Permission.storage.request();
  } catch (_) {
    // Best-effort only
  }
}

String _sanitizeFilename(String name) {
  var cleaned = name.trim().replaceAll(RegExp(r'[<>:"/\\|?*]'), '_');
  if (!cleaned.toLowerCase().endsWith('.pdf')) {
    cleaned = '$cleaned.pdf';
  }
  return cleaned;
}

Future<File> _uniqueFile(Directory dir, String filename) async {
  final base = filename.replaceFirst(RegExp(r'\.pdf$', caseSensitive: false), '');
  var candidate = File('${dir.path}/$filename');
  var n = 2;
  while (await candidate.exists() && n < 100) {
    candidate = File('${dir.path}/${base}_$n.pdf');
    n++;
  }
  return candidate;
}
