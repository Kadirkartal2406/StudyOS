import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/dashboard/data/models/dashboard_model.dart';

void main() {
  group('DashboardModel.fromJson', () {
    test('backend response alanlarını doğru parse eder', () {
      final json = {
        'first_name': 'Kadir',
        'daily_study_goal_minutes': 120,
        'today_study_minutes': 45,
        'today_questions_solved': 12,
        'today_studied_topic': 'Matematik',
        'daily_progress_percentage': 37.5,
        'last_login_at': '2026-07-15T10:00:00Z',
        'today_ai_recommendation': 'Ritmini koru',
        'today_ai_recommendation_code': 'keep_going',
        'today_ai_recommendation_reason': 'Kritik uyarı kuralı tetiklenmedi.',
        'active_exam_type': 'yks',
        'primary_exam_type': 'yks',
        'primary_target': {
          'exam_type': 'yks',
          'is_primary': true,
          'target_university': 'ODTÜ',
          'target_department': 'Bilgisayar',
          'target_net': 95,
        },
        'active_target': {
          'exam_type': 'yks',
          'is_primary': true,
          'target_university': 'ODTÜ',
          'target_department': 'Bilgisayar',
          'target_net': 95,
        },
        'next_action': {
          'title': 'TYT Matematik · Problemler',
          'subtitle': '25 dakika çalış',
          'reason': 'Bugünkü sıradaki çalışma bloğun.',
          'action_type': 'study_plan',
          'deep_link_hint': '/study-plan',
          'cta_label': 'Başla',
          'confidence_tone': 'high',
        },
        'today_context_lines': ['Bugün 2 çalışma bloğun kaldı'],
        'today_journey_line': 'YKS · 120 gün kaldı',
        'weekly_goals': [
          {
            'id': '11111111-1111-1111-1111-111111111111',
            'title': 'Haftalık Matematik',
            'progress': 40,
            'remaining': 180,
            'eta_hint': '3 gün',
            'goal_type': 'study_time',
            'status': 'active',
          },
        ],
      };

      final model = DashboardModel.fromJson(json);

      expect(model.firstName, 'Kadir');
      expect(model.dailyStudyGoalMinutes, 120);
      expect(model.todayStudyMinutes, 45);
      expect(model.todayQuestionsSolved, 12);
      expect(model.todayStudiedTopic, 'Matematik');
      expect(model.dailyProgressPercentage, 37.5);
      expect(model.lastLoginAt, DateTime.parse('2026-07-15T10:00:00Z'));
      expect(model.todayAiRecommendation, 'Ritmini koru');
      expect(model.todayAiRecommendationCode, 'keep_going');
      expect(model.todayAiRecommendationReason, 'Kritik uyarı kuralı tetiklenmedi.');
      expect(model.activeExamType, 'yks');
      expect(model.primaryTarget?.targetUniversity, 'ODTÜ');
      expect(model.primaryTarget?.targetDepartment, 'Bilgisayar');
      expect(model.toEntity().primaryTarget?.targetUniversity, 'ODTÜ');
      expect(model.nextAction?.title, 'TYT Matematik · Problemler');
      expect(model.nextAction?.actionType, 'study_plan');
      expect(model.toEntity().nextAction?.ctaLabel, 'Başla');
      expect(model.todayContextLines, ['Bugün 2 çalışma bloğun kaldı']);
      expect(model.todayJourneyLine, 'YKS · 120 gün kaldı');
      expect(model.weeklyGoals.length, 1);
      expect(model.weeklyGoals.first.title, 'Haftalık Matematik');
      expect(model.weeklyGoals.first.etaHint, '3 gün');
      expect(model.plannerDraftId, isNull);
      expect(model.plannerItemCount, 0);
    });

    test('planner_summary alanlarını parse eder', () {
      final json = {
        'first_name': 'Kadir',
        'daily_study_goal_minutes': 120,
        'today_study_minutes': 0,
        'today_questions_solved': 0,
        'today_studied_topic': null,
        'daily_progress_percentage': 0.0,
        'planner_summary': {
          'draft_id': '11111111-1111-1111-1111-111111111111',
          'status': 'draft',
          'target_exam': 'tyt',
          'target_net': 90.0,
          'item_count': 4,
          'overview_reason': 'Zayıf derslere odaklan',
        },
      };

      final model = DashboardModel.fromJson(json);

      expect(model.plannerDraftId, '11111111-1111-1111-1111-111111111111');
      expect(model.plannerStatus, 'draft');
      expect(model.plannerTargetExam, 'tyt');
      expect(model.plannerTargetNet, 90.0);
      expect(model.plannerItemCount, 4);
      expect(model.plannerOverviewReason, 'Zayıf derslere odaklan');
      expect(model.toEntity().plannerOverviewReason, 'Zayıf derslere odaklan');
    });

    test('null olabilen alanları doğru işler (placeholder değerler)', () {
      final json = {
        'first_name': 'Ayşe',
        'daily_study_goal_minutes': 120,
        'today_study_minutes': 0,
        'today_questions_solved': 0,
        'today_studied_topic': null,
        'daily_progress_percentage': 0.0,
        'last_login_at': null,
      };

      final model = DashboardModel.fromJson(json);

      expect(model.todayStudiedTopic, isNull);
      expect(model.lastLoginAt, isNull);
    });
  });

  group('DashboardModel.toEntity', () {
    test('tüm alanları eksiksiz entity\'e aktarır', () {
      const model = DashboardModel(
        firstName: 'Kadir',
        dailyStudyGoalMinutes: 120,
        todayStudyMinutes: 45,
        todayQuestionsSolved: 12,
        todayStudiedTopic: 'Fizik',
        dailyProgressPercentage: 37.5,
        lastLoginAt: null,
      );

      final entity = model.toEntity();

      expect(entity.firstName, model.firstName);
      expect(entity.dailyStudyGoalMinutes, model.dailyStudyGoalMinutes);
      expect(entity.todayStudyMinutes, model.todayStudyMinutes);
      expect(entity.todayQuestionsSolved, model.todayQuestionsSolved);
      expect(entity.todayStudiedTopic, model.todayStudiedTopic);
      expect(entity.dailyProgressPercentage, model.dailyProgressPercentage);
      expect(entity.todayAiRecommendation, isNull);
      expect(entity.weeklyGoals, isEmpty);
    });
  });
}
