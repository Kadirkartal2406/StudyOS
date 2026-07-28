/// Tahmini resmi sınav tarihleri (mobil geri sayım / onboarding).
library;

DateTime nextExamDate(String? examType, {DateTime? now}) {
  final today = now ?? DateTime.now();
  final key = (examType ?? 'kpss').toLowerCase().trim();
  const md = <String, List<int>>{
    'yks': [6, 21],
    'tyt': [6, 21],
    'ayt': [6, 22],
    'kpss': [9, 7],
    'lgs': [6, 15],
    'ales': [5, 4],
    'yds': [4, 6],
    'yokdil': [3, 16],
    'dgs': [7, 20],
    'ags': [7, 13],
  };
  final pair = md[key] ?? md['kpss']!;
  var candidate = DateTime(today.year, pair[0], pair[1]);
  final todayDate = DateTime(today.year, today.month, today.day);
  if (!candidate.isAfter(todayDate)) {
    candidate = DateTime(today.year + 1, pair[0], pair[1]);
  }
  return candidate;
}

String formatExamDateIso(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-'
    '${d.month.toString().padLeft(2, '0')}-'
    '${d.day.toString().padLeft(2, '0')}';
