import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/subjects/domain/subject_display_title.dart';

void main() {
  group('subjectDisplayTitle', () {
    test('TYT / AYT / KPSS / YDS prefixes', () {
      expect(
        subjectDisplayTitle(
          subjectCode: 'tyt_matematik',
          subjectName: 'Matematik',
          section: 'tyt',
        ),
        'TYT Matematik',
      );
      expect(
        subjectDisplayTitle(
          subjectCode: 'ayt_matematik',
          subjectName: 'Matematik',
          section: 'ayt',
        ),
        'AYT Matematik',
      );
      expect(
        subjectDisplayTitle(
          subjectCode: 'kpss_turkce',
          subjectName: 'Türkçe',
        ),
        'KPSS Türkçe',
      );
      expect(
        subjectDisplayTitle(
          subjectCode: 'yds_reading',
          subjectName: 'Reading',
        ),
        'YDS Reading',
      );
    });

    test('short name without known prefix stays plain', () {
      expect(
        subjectDisplayTitle(
          subjectCode: 'custom_foo',
          subjectName: 'Özel',
        ),
        'Özel',
      );
    });
  });
}
