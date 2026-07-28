import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/goal_engine/data/models/goal_models.dart';
import 'package:studyos_mobile/features/goal_engine/domain/entities/goal_entity.dart';

void main() {
  test('GoalModel.fromJson entity eşlemesi', () {
    final model = GoalModel.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'user_id': '22222222-2222-2222-2222-222222222222',
      'title': 'Haftalık Matematik',
      'description': 'Türev çalış',
      'goal_type': 'study_time',
      'target_value': 300,
      'current_value': 120,
      'progress': 40,
      'priority': 'high',
      'period': 'weekly',
      'status': 'active',
      'subject': 'Matematik',
      'topic': 'Türev',
      'start_date': '2026-07-13',
      'end_date': '2026-07-19',
      'completed_at': null,
      'metadata': {},
      'milestones_reached': ['25'],
      'remaining': 180,
      'eta_days': 3.5,
      'created_at': '2026-07-13T10:00:00Z',
      'updated_at': '2026-07-16T10:00:00Z',
    });

    final entity = model.toEntity();
    expect(entity.title, 'Haftalık Matematik');
    expect(entity.goalType, GoalType.studyTime);
    expect(entity.period, GoalPeriod.weekly);
    expect(entity.priority, GoalPriority.high);
    expect(entity.status, GoalStatus.active);
    expect(entity.progress, 40);
    expect(entity.milestonesReached, ['25']);
    expect(entity.etaDays, 3.5);
  });

  test('GoalProgressModel.fromJson özet alanları', () {
    final model = GoalProgressModel.fromJson({
      'items': [
        {
          'id': '11111111-1111-1111-1111-111111111111',
          'title': 'Pomodoro',
          'goal_type': 'pomodoro',
          'period': 'daily',
          'progress': 50,
          'current_value': 2,
          'target_value': 4,
          'remaining': 2,
          'eta_days': 1,
          'status': 'active',
          'milestones_reached': ['25', '50'],
        },
      ],
      'active_count': 1,
      'completed_count': 0,
      'average_progress': 50,
    });

    final entity = model.toEntity();
    expect(entity.activeCount, 1);
    expect(entity.averageProgress, 50);
    expect(entity.items.first.goalType, GoalType.pomodoro);
    expect(entity.items.first.milestonesReached, ['25', '50']);
  });
}
