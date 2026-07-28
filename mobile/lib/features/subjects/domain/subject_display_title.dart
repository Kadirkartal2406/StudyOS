/// Sprint-3.1.C.x — Hub / list title: TYT Matematik, KPSS Türkçe, …
String subjectDisplayTitle({
  required String subjectCode,
  required String subjectName,
  String? section,
}) {
  final name = subjectName.trim();
  final code = subjectCode.trim().toLowerCase();
  final sec = section?.trim().toLowerCase();

  if (sec == 'tyt' || code.startsWith('tyt_')) {
    return 'TYT $name';
  }
  if (sec == 'ayt' || code.startsWith('ayt_')) {
    return 'AYT $name';
  }
  if (code.startsWith('kpss_')) {
    return 'KPSS $name';
  }
  if (code.startsWith('yds_')) {
    return 'YDS $name';
  }
  if (code.startsWith('lgs_')) {
    return 'LGS $name';
  }
  return name;
}
