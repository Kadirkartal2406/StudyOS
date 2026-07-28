import 'dart:html' as html;
import 'dart:typed_data';

Future<String> savePdfBytes(List<int> bytes, String filename) async {
  final data = Uint8List.fromList(bytes);
  final blob = html.Blob([data], 'application/pdf');
  final url = html.Url.createObjectUrlFromBlob(blob);
  html.AnchorElement(href: url)
    ..setAttribute('download', filename)
    ..click();
  html.Url.revokeObjectUrl(url);
  return filename;
}
