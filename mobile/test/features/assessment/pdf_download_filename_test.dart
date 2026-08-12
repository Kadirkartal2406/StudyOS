import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/assessment/presentation/utils/pdf_download.dart';

void main() {
  test('buildDailyBookletFilename formats exam and date', () {
    final name = buildDailyBookletFilename(
      examType: 'tyt',
      date: DateTime(2026, 8, 12),
    );
    expect(name, 'StudyOS_TYT_Gunluk_Deneme_12-08-2026.pdf');
  });

  test('buildDailyBookletFilename sanitizes odd exam codes', () {
    final name = buildDailyBookletFilename(
      examType: 'yds_ingilizce',
      date: DateTime(2026, 1, 5),
    );
    expect(name, 'StudyOS_YDS_INGILIZCE_Gunluk_Deneme_05-01-2026.pdf');
  });

  test('parseChallengeDate reads iso date', () {
    expect(parseChallengeDate('2026-08-12'), DateTime(2026, 8, 12));
    expect(parseChallengeDate(null), isNull);
  });
}
