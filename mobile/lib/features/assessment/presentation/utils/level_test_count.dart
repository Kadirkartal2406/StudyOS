/// Seviye testi soru sayısı — sınava göre (ders başına).
int levelTestCountForExam(String? examType) {
  switch ((examType ?? '').toLowerCase().trim()) {
    case 'kpss':
    case 'ags':
      return 12;
    case 'yks':
    case 'tyt':
    case 'ayt':
    case 'dgs':
      return 10;
    case 'lgs':
      return 10;
    case 'ales':
      return 12;
    case 'yds':
    case 'yokdil':
      return 15;
    default:
      return 10;
  }
}
