import 'dart:io';

Future<String> savePdfBytes(List<int> bytes, String filename) async {
  Directory? downloadDir;

  if (Platform.isAndroid) {
    final publicDownload = Directory('/storage/emulated/0/Download');
    if (await publicDownload.exists()) {
      downloadDir = publicDownload;
    }
  }

  downloadDir ??= Directory.systemTemp;

  final filePath = '${downloadDir.path}/$filename';
  final file = File(filePath);
  await file.writeAsBytes(bytes, flush: true);
  return file.path;
}
