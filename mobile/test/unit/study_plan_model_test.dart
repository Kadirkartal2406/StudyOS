import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/study_plan/data/models/study_plan_model.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_plan_status.dart';

Map<String, dynamic> _json({Map<String, dynamic>? overrides}) {
  final base = <String, dynamic>{
    'id': 'plan-1',
    'user_id': 'user-1',
    'title': 'Matematik Çalışması',
    'subject': 'Matematik',
    'topic': 'Türev',
    'target_question_count': 20,
    'estimated_minutes': 60,
    'planned_start_time': '09:00:00',
    'planned_end_time': '10:00:00',
    'status': 'planned',
    'completed_question_count': 0,
    'completed_minutes': 0,
    'order_index': 0,
    'study_date': '2026-07-16',
    'created_at': '2026-07-16T08:00:00Z',
    'updated_at': '2026-07-16T08:00:00Z',
  };
  base.addAll(overrides ?? {});
  return base;
}

void main() {
  group('StudyPlanModel.fromJson', () {
    test('backend response alanlarını doğru parse eder', () {
      final model = StudyPlanModel.fromJson(_json());

      expect(model.id, 'plan-1');
      expect(model.title, 'Matematik Çalışması');
      expect(model.subject, 'Matematik');
      expect(model.topic, 'Türev');
      expect(model.targetQuestionCount, 20);
      expect(model.estimatedMinutes, 60);
      expect(model.plannedStartTime, '09:00:00');
      expect(model.plannedEndTime, '10:00:00');
      expect(model.status, 'planned');
      expect(model.orderIndex, 0);
    });

    test('nullable alanları doğru işler (topic ve saat aralığı yok)', () {
      final json = _json(
        overrides: {
          'topic': null,
          'planned_start_time': null,
          'planned_end_time': null,
        },
      );

      final model = StudyPlanModel.fromJson(json);

      expect(model.topic, isNull);
      expect(model.plannedStartTime, isNull);
      expect(model.plannedEndTime, isNull);
    });
  });

  group('StudyPlanModel.toEntity', () {
    test('saat alanlarını StudyTime\'a, statüyü enum\'a dönüştürür', () {
      final model = StudyPlanModel.fromJson(_json());

      final entity = model.toEntity();

      expect(entity.plannedStartTime?.hour, 9);
      expect(entity.plannedStartTime?.minute, 0);
      expect(entity.plannedEndTime?.label, '10:00');
      expect(entity.status, StudyPlanStatus.planned);
      expect(entity.hasTimeRange, isTrue);
    });

    test('completed durumunda progressPercentage doğru hesaplanır', () {
      final json = _json(
        overrides: {
          'status': 'completed',
          'completed_minutes': 30,
          'estimated_minutes': 60,
        },
      );

      final entity = StudyPlanModel.fromJson(json).toEntity();

      expect(entity.status, StudyPlanStatus.completed);
      expect(entity.progressPercentage, 50.0);
    });

    test('in_progress ve skipped statüleri doğru dönüştürülür', () {
      final inProgress =
          StudyPlanModel.fromJson(_json(overrides: {'status': 'in_progress'}))
              .toEntity();
      final skipped =
          StudyPlanModel.fromJson(_json(overrides: {'status': 'skipped'}))
              .toEntity();

      expect(inProgress.status, StudyPlanStatus.inProgress);
      expect(skipped.status, StudyPlanStatus.skipped);
      expect(skipped.status.isTerminal, isTrue);
      expect(inProgress.status.isTerminal, isFalse);
    });
  });
}
