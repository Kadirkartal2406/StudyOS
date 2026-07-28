import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/study_session/data/models/study_session_model.dart';
import 'package:studyos_mobile/features/study_session/domain/entities/study_session_status.dart';

void main() {
  group('StudySessionModel', () {
    final json = {
      'id': '11111111-1111-1111-1111-111111111111',
      'user_id': '22222222-2222-2222-2222-222222222222',
      'study_plan_id': null,
      'started_at': '2026-07-16T10:00:00Z',
      'ended_at': '2026-07-16T10:25:00Z',
      'planned_duration_minutes': 25,
      'actual_duration_minutes': 25,
      'break_duration_minutes': 5,
      'completed_questions': 10,
      'completed_topics': 1,
      'status': 'completed',
      'created_at': '2026-07-16T10:00:00Z',
      'updated_at': '2026-07-16T10:25:00Z',
    };

    test('fromJson parses fields', () {
      final model = StudySessionModel.fromJson(json);

      expect(model.id, json['id']);
      expect(model.plannedDurationMinutes, 25);
      expect(model.breakDurationMinutes, 5);
      expect(model.status, 'completed');
      expect(model.studyPlanId, isNull);
    });

    test('toEntity maps status enum', () {
      final entity = StudySessionModel.fromJson(json).toEntity();

      expect(entity.status, StudySessionStatus.completed);
      expect(entity.completedQuestions, 10);
      expect(entity.isActive, isFalse);
    });

    test('running status is active', () {
      final running = Map<String, dynamic>.from(json)
        ..['status'] = 'running'
        ..['ended_at'] = null;
      final entity = StudySessionModel.fromJson(running).toEntity();

      expect(entity.status, StudySessionStatus.running);
      expect(entity.isActive, isTrue);
    });
  });
}
