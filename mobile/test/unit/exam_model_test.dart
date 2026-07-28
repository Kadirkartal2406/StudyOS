import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/exam_tracking/data/models/exam_model.dart';

void main() {
  test('ExamModel.fromJson maps nested results', () {
    final model = ExamModel.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'user_id': '22222222-2222-2222-2222-222222222222',
      'title': 'TYT Deneme',
      'exam_type': 'tyt',
      'exam_date': '2026-07-12',
      'duration_minutes': 135,
      'notes': null,
      'total_net': 28.5,
      'total_questions': 40,
      'result_count': 1,
      'results': [
        {
          'id': '33333333-3333-3333-3333-333333333333',
          'exam_id': '11111111-1111-1111-1111-111111111111',
          'subject': 'Matematik',
          'correct_count': 30,
          'wrong_count': 8,
          'blank_count': 2,
          'question_count': 40,
          'net_score': 28.0,
          'duration_minutes': 60,
          'created_at': '2026-07-12T10:00:00Z',
          'updated_at': '2026-07-12T10:00:00Z',
        },
      ],
      'created_at': '2026-07-12T10:00:00Z',
      'updated_at': '2026-07-12T10:00:00Z',
    });

    expect(model.title, 'TYT Deneme');
    expect(model.examType, 'tyt');
    expect(model.results, hasLength(1));
    expect(model.results.first.subject, 'Matematik');
    expect(model.toEntity().totalNet, 28.5);
  });
}
