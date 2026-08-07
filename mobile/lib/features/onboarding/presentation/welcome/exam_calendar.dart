/// Tahmini resmi sınav tarihleri (mobil geri sayım / onboarding).
library;

DateTime nextExamDate(String? examType, {String? branch, DateTime? now}) {
  final today = now ?? DateTime.now();
  final key = (examType ?? 'kpss').toLowerCase().trim();
  final b = (branch ?? '').toLowerCase().trim();
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
    'kpss_lisans': [7, 12],
    'kpss_onlisans': [10, 11],
    'kpss_ortaogretim': [11, 8],
  };
  
  String searchKey = key;
  if (key == 'kpss') {
    if (b.contains('onlisans') || b.contains('önlisans')) {
      searchKey = 'kpss_onlisans';
    } else if (b.contains('orta') || b.contains('lise')) {
      searchKey = 'kpss_ortaogretim';
    } else if (b.contains('lisans')) {
      searchKey = 'kpss_lisans';
    }
  }

  final pair = md[searchKey] ?? md['kpss']!;
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
