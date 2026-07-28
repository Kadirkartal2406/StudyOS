import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/ai_coach/data/models/ai_coach_models.dart';

void main() {
  group('AiOverviewModel', () {
    test('fromJson parses overview and recommendation', () {
      final model = AiOverviewModel.fromJson({
        'has_enough_data': true,
        'streak_days': 4,
        'average_daily_minutes': 42.5,
        'average_daily_questions': 12.0,
        'most_studied_subject': 'Matematik',
        'correct_rate': 68.2,
        'pomodoro_completion_rate': 80.0,
        'idle_days_last_14': 3,
        'recommendations_count': 2,
        'top_recommendation': {
          'code': 'keep_going',
          'message': 'Harika gidiyorsun',
          'priority': 10,
          'category': 'motivation',
        },
      });

      final entity = model.toEntity();
      expect(entity.hasEnoughData, isTrue);
      expect(entity.streakDays, 4);
      expect(entity.mostStudiedSubject, 'Matematik');
      expect(entity.topRecommendation?.code, 'keep_going');
      expect(entity.topRecommendation?.message, 'Harika gidiyorsun');
    });
  });

  group('AiPerformanceModel', () {
    test('fromJson maps subjects', () {
      final model = AiPerformanceModel.fromJson({
        'correct_rate': 50.0,
        'wrong_rate': 40.0,
        'total_net': 8.0,
        'total_questions': 20,
        'pomodoro_completion_rate': 70.0,
        'total_pomodoros': 3,
        'subjects_by_accuracy': [
          {
            'key': 'acc_Matematik',
            'label': 'Matematik',
            'value': 50.0,
            'unit': '%',
          },
        ],
        'subjects_by_questions': [
          {
            'key': 'q_Matematik',
            'label': 'Matematik',
            'value': 20,
            'unit': 'soru',
          },
        ],
      });

      expect(model.toEntity().totalQuestions, 20);
      expect(model.toEntity().subjectsByAccuracy.first.label, 'Matematik');
    });
  });

  group('AiTrendsModel', () {
    test('fromJson maps daily series and deltas', () {
      final model = AiTrendsModel.fromJson({
        'weekly_study_minutes': 100,
        'previous_week_study_minutes': 80,
        'study_minutes_delta_pct': 25.0,
        'weekly_questions': 40,
        'previous_week_questions': 20,
        'questions_delta_pct': 100.0,
        'monthly_study_minutes': 300,
        'previous_month_study_minutes': 250,
        'daily_series': [
          {'label': 'Pzt', 'study_minutes': 30, 'question_count': 10},
        ],
      });

      final entity = model.toEntity();
      expect(entity.studyMinutesDeltaPct, 25.0);
      expect(entity.dailySeries, hasLength(1));
      expect(entity.dailySeries.first.questionCount, 10);
    });
  });
}
