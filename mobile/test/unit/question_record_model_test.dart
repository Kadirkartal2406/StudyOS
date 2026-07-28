import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/question_tracking/data/models/question_record_model.dart';
import 'package:studyos_mobile/features/question_tracking/domain/entities/question_enums.dart';

void main() {
  test('QuestionRecordModel.fromJson entity eşlemesi', () {
    final model = QuestionRecordModel.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'user_id': '22222222-2222-2222-2222-222222222222',
      'study_plan_id': null,
      'study_session_id': null,
      'subject': 'Matematik',
      'topic': 'Türev',
      'question_count': 20,
      'correct_count': 12,
      'wrong_count': 5,
      'blank_count': 3,
      'duration_minutes': 40,
      'difficulty': 'medium',
      'source': 'book',
      'exam_type': 'tyt',
      'note': null,
      'net_score': '10.75',
      'created_at': '2026-07-16T10:00:00Z',
      'updated_at': '2026-07-16T10:00:00Z',
    });

    final entity = model.toEntity();
    expect(entity.subject, 'Matematik');
    expect(entity.netScore, 10.75);
    expect(entity.difficulty, QuestionDifficulty.medium);
    expect(entity.examType, ExamType.tyt);
    expect(entity.source, QuestionSource.book);
  });

  test('parseNetScore string ve num', () {
    expect(parseNetScore('7.50'), 7.5);
    expect(parseNetScore(3), 3.0);
  });
}
