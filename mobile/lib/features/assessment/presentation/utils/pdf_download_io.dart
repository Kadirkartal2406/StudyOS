import 'dart:io';

Future<String> savePdfBytes(List<int> bytes, String filename) async {
  final file = File('${Directory.systemTemp.path}/$filename');
  await file.writeAsBytes(bytes, flush: true);
  return file.path;
}
