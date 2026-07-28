import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/statistics/data/models/statistics_models.dart';

void main() {
  test('StatisticsOverviewModel.fromJson parses fields', () {
    final model = StatisticsOverviewModel.fromJson({
      'total_study_minutes': 120,
      'today_study_minutes': 25,
      'today_questions': 8,
      'week_study_minutes': 60,
      'month_study_minutes': 100,
      'total_sessions': 4,
      'total_pomodoros': 4,
      'completed_plans': 2,
      'total_questions': 40,
      'average_session_minutes': 30.5,
      'longest_session_minutes': 50,
      'most_studied_subject': 'Matematik',
      'most_studied_topic': 'Türev',
      'streak_days': 3,
      'most_productive_weekday_label': 'Salı',
      'most_productive_hour': 10,
    });

    final entity = model.toEntity();
    expect(entity.totalStudyMinutes, 120);
    expect(entity.streakDays, 3);
    expect(entity.mostStudiedSubject, 'Matematik');
    expect(entity.averageSessionMinutes, 30.5);
  });

  test('StatisticsDistributionModel.fromJson maps items', () {
    final model = StatisticsDistributionModel.fromJson({
      'total_minutes': 50,
      'items': [
        {
          'name': 'Fizik',
          'study_minutes': 50,
          'session_count': 2,
          'question_count': 10,
          'percentage': 100.0,
        },
      ],
    });

    expect(model.items, hasLength(1));
    expect(model.toEntity().items.first.name, 'Fizik');
  });
}
