import '../../domain/entities/activity_entity.dart';
import '../../domain/entities/dashboard_entity.dart';

class ActivityModel {
  const ActivityModel({
    required this.id,
    required this.eventType,
    required this.title,
    required this.occurredAt,
    this.description,
    this.studySessionId,
    this.studyPlanId,
  });

  final String id;
  final String eventType;
  final String title;
  final String? description;
  final String? studySessionId;
  final String? studyPlanId;
  final DateTime occurredAt;

  factory ActivityModel.fromJson(Map<String, dynamic> json) {
    return ActivityModel(
      id: json['id'] as String,
      eventType: json['event_type'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      studySessionId: json['study_session_id'] as String?,
      studyPlanId: json['study_plan_id'] as String?,
      occurredAt: DateTime.parse(json['occurred_at'] as String),
    );
  }

  ActivityEntity toEntity() => ActivityEntity(
        id: id,
        eventType: eventType,
        title: title,
        description: description,
        studySessionId: studySessionId,
        studyPlanId: studyPlanId,
        occurredAt: occurredAt,
      );
}

class WeeklyGoalSummaryModel {
  const WeeklyGoalSummaryModel({
    required this.id,
    required this.title,
    required this.progress,
    required this.remaining,
    required this.goalType,
    required this.status,
    this.etaHint,
    this.currentValue = 0,
    this.targetValue = 0,
    this.estimatedCompletion,
    this.productGoalType,
  });

  final String id;
  final String title;
  final double progress;
  final double remaining;
  final double currentValue;
  final double targetValue;
  final String? etaHint;
  final String? estimatedCompletion;
  final String goalType;
  final String? productGoalType;
  final String status;

  factory WeeklyGoalSummaryModel.fromJson(Map<String, dynamic> json) {
    return WeeklyGoalSummaryModel(
      id: json['id'] as String,
      title: json['title'] as String,
      progress: (json['progress'] as num?)?.toDouble() ?? 0,
      remaining: (json['remaining'] as num?)?.toDouble() ?? 0,
      currentValue: (json['current_value'] as num?)?.toDouble() ?? 0,
      targetValue: (json['target_value'] as num?)?.toDouble() ?? 0,
      etaHint: json['eta_hint'] as String?,
      estimatedCompletion: json['estimated_completion'] as String?,
      goalType: json['goal_type'] as String? ?? 'custom',
      productGoalType: json['product_goal_type'] as String?,
      status: json['status'] as String? ?? 'active',
    );
  }

  WeeklyGoalSummaryEntity toEntity() => WeeklyGoalSummaryEntity(
        id: id,
        title: title,
        progress: progress,
        remaining: remaining,
        currentValue: currentValue,
        targetValue: targetValue,
        etaHint: etaHint,
        estimatedCompletion: estimatedCompletion,
        goalType: goalType,
        productGoalType: productGoalType,
        status: status,
      );
}

/// API'den gelen `/dashboard` yanıtını parse eden model.
class DashboardModel {
  const DashboardModel({
    required this.firstName,
    required this.dailyStudyGoalMinutes,
    required this.todayStudyMinutes,
    required this.todayQuestionsSolved,
    required this.dailyProgressPercentage,
    this.todayStudiedTopic,
    this.lastLoginAt,
    this.todayPlanCount = 0,
    this.completedPlanCount = 0,
    this.streakDays = 0,
    this.totalPomodoros = 0,
    this.totalStudyMinutes = 0,
    this.averageSessionMinutes = 0,
    this.mostStudiedSubject,
    this.weekStudyMinutes = 0,
    this.recentActivities = const [],
    this.todayAiRecommendation,
    this.todayAiRecommendationCode,
    this.todayAiRecommendationReason,
    this.weeklyGoals = const [],
    this.todayResourcesOpened = 0,
    this.todayResourcesCompleted = 0,
    this.recentResourceTitles = const [],
    this.lastExamTitle,
    this.lastExamNet,
    this.lastExamDeltaNet,
    this.lastExamDate,
    this.todayAiExamSummary,
    this.plannerDraftId,
    this.plannerStatus,
    this.plannerTargetExam,
    this.plannerTargetNet,
    this.plannerItemCount = 0,
    this.plannerOverviewReason,
    this.revisionDueToday = 0,
    this.revisionOverdue = 0,
    this.revisionDueThisWeek = 0,
    this.revisionNextTitle,
    this.revisionOverviewReason,
    this.achievementTotalUnlocked = 0,
    this.achievementTotalPoints = 0,
    this.achievementRecentTitle,
    this.achievementRecentReason,
    this.journeyTodayPct = 0,
    this.journeyWeekPct = 0,
    this.journeyMonthPct = 0,
    this.journeyOverallPct = 0,
    this.journeyStage = 'new_user',
    this.journeyOnboardingRequired = false,
    this.journeyPrimaryExamType,
    this.journeyDaysRemaining,
    this.journeyExamDate,
    this.journeyBaselineLevel,
    this.assessmentProgressPct = 0,
    this.assessmentMessage,
    this.mySubjectNames = const [],
    this.mySubjectCodes = const [],
    this.subjectsMostStudied,
    this.subjectsWeakest,
    this.subjectsLongestIdle,
    this.subjectsTodayStudiedCount = 0,
    this.activeExamType,
    this.primaryExamType,
    this.primaryTarget,
    this.activeTarget,
    this.nextAction,
    this.todayContextLines = const [],
    this.todayJourneyLine,
    this.observationState = 'full',
    this.learningFeed = const [],
    this.insightCards = const [],
    this.coachToday,
    this.confidenceSummary = const [],
    this.livingPlanSuggestion,
  });

  final String firstName;
  final int dailyStudyGoalMinutes;
  final int todayStudyMinutes;
  final int todayQuestionsSolved;
  final String? todayStudiedTopic;
  final double dailyProgressPercentage;
  final DateTime? lastLoginAt;
  final int todayPlanCount;
  final int completedPlanCount;
  final int streakDays;
  final int totalPomodoros;
  final int totalStudyMinutes;
  final double averageSessionMinutes;
  final String? mostStudiedSubject;
  final int weekStudyMinutes;
  final List<ActivityModel> recentActivities;
  final String? todayAiRecommendation;
  final String? todayAiRecommendationCode;
  final String? todayAiRecommendationReason;
  final List<WeeklyGoalSummaryModel> weeklyGoals;
  final int todayResourcesOpened;
  final int todayResourcesCompleted;
  final List<String> recentResourceTitles;
  final String? lastExamTitle;
  final double? lastExamNet;
  final double? lastExamDeltaNet;
  final DateTime? lastExamDate;
  final String? todayAiExamSummary;
  final String? plannerDraftId;
  final String? plannerStatus;
  final String? plannerTargetExam;
  final double? plannerTargetNet;
  final int plannerItemCount;
  final String? plannerOverviewReason;
  final int revisionDueToday;
  final int revisionOverdue;
  final int revisionDueThisWeek;
  final String? revisionNextTitle;
  final String? revisionOverviewReason;
  final int achievementTotalUnlocked;
  final int achievementTotalPoints;
  final String? achievementRecentTitle;
  final String? achievementRecentReason;
  final double journeyTodayPct;
  final double journeyWeekPct;
  final double journeyMonthPct;
  final double journeyOverallPct;
  final String journeyStage;
  final bool journeyOnboardingRequired;
  final String? journeyPrimaryExamType;
  final int? journeyDaysRemaining;
  final DateTime? journeyExamDate;
  final String? journeyBaselineLevel;
  final double assessmentProgressPct;
  final String? assessmentMessage;
  final List<String> mySubjectNames;
  final List<String> mySubjectCodes;
  final String? subjectsMostStudied;
  final String? subjectsWeakest;
  final String? subjectsLongestIdle;
  final int subjectsTodayStudiedCount;
  final String? activeExamType;
  final String? primaryExamType;
  final DashboardExamTargetModel? primaryTarget;
  final DashboardExamTargetModel? activeTarget;
  final NextActionModel? nextAction;
  final List<String> todayContextLines;
  final String? todayJourneyLine;
  final String observationState;
  final List<FeedCardEntity> learningFeed;
  final List<InsightCardEntity> insightCards;
  final CoachTodayEntity? coachToday;
  final List<TopicConfidenceSummaryEntity> confidenceSummary;
  final LivingPlanSuggestionEntity? livingPlanSuggestion;

  factory DashboardModel.fromJson(Map<String, dynamic> json) {
    final activitiesJson = json['recent_activities'] as List<dynamic>? ?? [];
    final weeklyGoalsJson = json['weekly_goals'] as List<dynamic>? ?? [];
    final recentResourcesJson =
        json['recent_resources'] as List<dynamic>? ?? [];
    final mySubjectsJson = json['my_subjects'] as List<dynamic>? ?? [];
    final subjectsSummary = json['subjects_summary'] as Map<String, dynamic>?;
    final planner = json['planner_summary'] as Map<String, dynamic>?;
    final revision = json['revision_summary'] as Map<String, dynamic>?;
    final achievement = json['achievement_summary'] as Map<String, dynamic>?;
    final journey = json['journey_progress'] as Map<String, dynamic>?;
    final primaryTargetJson = json['primary_target'] as Map<String, dynamic>?;
    final activeTargetJson = json['active_target'] as Map<String, dynamic>?;
    final nextActionJson = json['next_action'] as Map<String, dynamic>?;
    final contextLinesJson = json['today_context_lines'] as List<dynamic>? ?? [];
    final coachJson = json['coach_today'] as Map<String, dynamic>?;
    CoachTodayEntity? coachToday;
    if (coachJson != null) {
      final win = coachJson['win'] as Map<String, dynamic>?;
      final reasons = (coachJson['reasons'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map((r) => r['detail'] as String? ?? r['label'] as String? ?? '')
          .where((s) => s.isNotEmpty)
          .toList();
      coachToday = CoachTodayEntity(
        headline: coachJson['headline'] as String? ?? '',
        body: coachJson['body'] as String? ?? '',
        focusTopic: coachJson['focus_topic'] as String?,
        suggestedMinutes: coachJson['suggested_minutes'] as int?,
        habitHint: coachJson['habit_hint'] as String?,
        deepLinkHint: coachJson['deep_link_hint'] as String?,
        ctaLabel: coachJson['cta_label'] as String? ?? 'Başla',
        winTitle: win?['title'] as String?,
        winMessage: win?['message'] as String?,
        reasons: reasons,
      );
    }

    final confJson = json['confidence_summary'] as List<dynamic>? ?? [];
    final confSummary = confJson
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => TopicConfidenceSummaryEntity(
            topicCode: m['topic_code'] as String? ?? '',
            subjectCode: m['subject_code'] as String? ?? '',
            topicName: m['topic_name'] as String?,
            belief: (m['belief'] as num?)?.toDouble() ?? 0.0,
            uncertainty: (m['uncertainty'] as num?)?.toDouble() ?? 1.0,
            confidenceLevel: m['confidence_level'] as String? ?? 'unknown',
            trendDirection: (m['trend_direction'] as num?)?.toDouble() ?? 0.0,
          ),
        )
        .toList();

    final lpJson = json['living_plan_suggestion'] as Map<String, dynamic>?;
    LivingPlanSuggestionEntity? lpSuggestion;
    if (lpJson != null) {
      lpSuggestion = LivingPlanSuggestionEntity(
        draftId: lpJson['draft_id'] as String? ?? '',
        topicCode: lpJson['topic_code'] as String?,
        topicName: lpJson['topic_name'] as String?,
        reason: lpJson['reason'] as String? ?? '',
        estimatedMinutes: lpJson['estimated_minutes'] as int? ?? 45,
      );
    }
    return DashboardModel(
      firstName: json['first_name'] as String,
      dailyStudyGoalMinutes: json['daily_study_goal_minutes'] as int,
      todayStudyMinutes: json['today_study_minutes'] as int,
      todayQuestionsSolved: json['today_questions_solved'] as int,
      todayStudiedTopic: json['today_studied_topic'] as String?,
      dailyProgressPercentage:
          (json['daily_progress_percentage'] as num).toDouble(),
      lastLoginAt: json['last_login_at'] == null
          ? null
          : DateTime.parse(json['last_login_at'] as String),
      todayPlanCount: json['today_plan_count'] as int? ?? 0,
      completedPlanCount: json['completed_plan_count'] as int? ?? 0,
      streakDays: json['streak_days'] as int? ?? 0,
      totalPomodoros: json['total_pomodoros'] as int? ?? 0,
      totalStudyMinutes: json['total_study_minutes'] as int? ?? 0,
      averageSessionMinutes:
          (json['average_session_minutes'] as num?)?.toDouble() ?? 0,
      mostStudiedSubject: json['most_studied_subject'] as String?,
      weekStudyMinutes: json['week_study_minutes'] as int? ?? 0,
      recentActivities: activitiesJson
          .map((e) => ActivityModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      todayAiRecommendation: json['today_ai_recommendation'] as String?,
      todayAiRecommendationCode:
          json['today_ai_recommendation_code'] as String?,
      todayAiRecommendationReason:
          json['today_ai_recommendation_reason'] as String?,
      weeklyGoals: weeklyGoalsJson
          .map(
            (e) => WeeklyGoalSummaryModel.fromJson(e as Map<String, dynamic>),
          )
          .toList(),
      todayResourcesOpened: json['today_resources_opened'] as int? ?? 0,
      todayResourcesCompleted: json['today_resources_completed'] as int? ?? 0,
      recentResourceTitles: recentResourcesJson
          .map((e) => (e as Map)['title']?.toString() ?? '')
          .where((t) => t.isNotEmpty)
          .toList(),
      lastExamTitle: json['last_exam_title'] as String?,
      lastExamNet: (json['last_exam_net'] as num?)?.toDouble(),
      lastExamDeltaNet: (json['last_exam_delta_net'] as num?)?.toDouble(),
      lastExamDate: json['last_exam_date'] == null
          ? null
          : DateTime.parse(json['last_exam_date'] as String),
      todayAiExamSummary: json['today_ai_exam_summary'] as String?,
      plannerDraftId: planner?['draft_id'] as String?,
      plannerStatus: planner?['status'] as String?,
      plannerTargetExam: planner?['target_exam'] as String?,
      plannerTargetNet: (planner?['target_net'] as num?)?.toDouble(),
      plannerItemCount: planner?['item_count'] as int? ?? 0,
      plannerOverviewReason: planner?['overview_reason'] as String?,
      revisionDueToday: revision?['due_today'] as int? ?? 0,
      revisionOverdue: revision?['overdue'] as int? ?? 0,
      revisionDueThisWeek: revision?['due_this_week'] as int? ?? 0,
      revisionNextTitle: revision?['next_title'] as String?,
      revisionOverviewReason: revision?['overview_reason'] as String?,
      achievementTotalUnlocked: achievement?['total_unlocked'] as int? ?? 0,
      achievementTotalPoints: achievement?['total_points'] as int? ?? 0,
      achievementRecentTitle: achievement?['recent_title'] as String?,
      achievementRecentReason: achievement?['recent_reason'] as String?,
      journeyTodayPct: (journey?['today_pct'] as num?)?.toDouble() ?? 0,
      journeyWeekPct: (journey?['week_pct'] as num?)?.toDouble() ?? 0,
      journeyMonthPct: (journey?['month_pct'] as num?)?.toDouble() ?? 0,
      journeyOverallPct: (journey?['overall_pct'] as num?)?.toDouble() ?? 0,
      journeyStage: journey?['journey_stage'] as String? ?? 'new_user',
      journeyOnboardingRequired:
          journey?['onboarding_required'] as bool? ?? false,
      journeyPrimaryExamType: journey?['primary_exam_type'] as String?,
      journeyDaysRemaining: journey?['days_remaining'] as int?,
      journeyExamDate: journey?['exam_date'] == null
          ? null
          : DateTime.tryParse(journey!['exam_date'] as String),
      journeyBaselineLevel: journey?['baseline_level'] as String?,
      assessmentProgressPct:
          (journey?['assessment_progress_pct'] as num?)?.toDouble() ?? 0,
      assessmentMessage: journey?['assessment_message'] as String?,
      mySubjectNames: mySubjectsJson
          .map((e) => (e as Map)['subject_name']?.toString() ?? '')
          .where((t) => t.isNotEmpty)
          .toList(),
      mySubjectCodes: mySubjectsJson
          .map((e) => (e as Map)['subject_code']?.toString() ?? '')
          .where((t) => t.isNotEmpty)
          .toList(),
      subjectsMostStudied: subjectsSummary?['most_studied_subject'] as String?,
      subjectsWeakest: subjectsSummary?['weakest_subject'] as String?,
      subjectsLongestIdle: subjectsSummary?['longest_idle_subject'] as String?,
      subjectsTodayStudiedCount:
          subjectsSummary?['today_studied_count'] as int? ?? 0,
      activeExamType: json['active_exam_type'] as String?,
      primaryExamType: json['primary_exam_type'] as String?,
      primaryTarget: primaryTargetJson == null
          ? null
          : DashboardExamTargetModel.fromJson(primaryTargetJson),
      activeTarget: activeTargetJson == null
          ? null
          : DashboardExamTargetModel.fromJson(activeTargetJson),
      nextAction: nextActionJson == null
          ? null
          : NextActionModel.fromJson(nextActionJson),
      todayContextLines: contextLinesJson
          .map((e) => e.toString())
          .where((t) => t.isNotEmpty)
          .toList(),
      todayJourneyLine: json['today_journey_line'] as String?,
      observationState: json['observation_state'] as String? ?? 'full',
      learningFeed: (json['learning_feed'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(
            (m) => FeedCardEntity(
              id: m['id'] as String? ?? '',
              title: m['title'] as String? ?? '',
              subtitle: m['subtitle'] as String? ?? '',
              kind: m['kind'] as String? ?? 'insight',
              deepLinkHint: m['deep_link_hint'] as String?,
              tone: m['tone'] as String? ?? 'neutral',
              subjectCode: m['subject_code'] as String?,
              topicCode: m['topic_code'] as String?,
            ),
          )
          .toList(),
      insightCards: (json['insight_cards'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(
            (m) => InsightCardEntity(
              id: m['id'] as String? ?? '',
              code: m['code'] as String? ?? '',
              message: m['message'] as String? ?? '',
              tone: m['tone'] as String? ?? 'neutral',
              deepLinkHint: m['deep_link_hint'] as String?,
            ),
          )
          .toList(),
      coachToday: coachToday,
      confidenceSummary: confSummary,
      livingPlanSuggestion: lpSuggestion,
    );
  }

  DashboardEntity toEntity() {
    return DashboardEntity(
      firstName: firstName,
      dailyStudyGoalMinutes: dailyStudyGoalMinutes,
      todayStudyMinutes: todayStudyMinutes,
      todayQuestionsSolved: todayQuestionsSolved,
      todayStudiedTopic: todayStudiedTopic,
      dailyProgressPercentage: dailyProgressPercentage,
      lastLoginAt: lastLoginAt,
      todayPlanCount: todayPlanCount,
      completedPlanCount: completedPlanCount,
      streakDays: streakDays,
      totalPomodoros: totalPomodoros,
      totalStudyMinutes: totalStudyMinutes,
      averageSessionMinutes: averageSessionMinutes,
      mostStudiedSubject: mostStudiedSubject,
      weekStudyMinutes: weekStudyMinutes,
      recentActivities: recentActivities.map((e) => e.toEntity()).toList(),
      todayAiRecommendation: todayAiRecommendation,
      todayAiRecommendationCode: todayAiRecommendationCode,
      todayAiRecommendationReason: todayAiRecommendationReason,
      weeklyGoals: weeklyGoals.map((e) => e.toEntity()).toList(),
      todayResourcesOpened: todayResourcesOpened,
      todayResourcesCompleted: todayResourcesCompleted,
      recentResourceTitles: recentResourceTitles,
      lastExamTitle: lastExamTitle,
      lastExamNet: lastExamNet,
      lastExamDeltaNet: lastExamDeltaNet,
      lastExamDate: lastExamDate,
      todayAiExamSummary: todayAiExamSummary,
      plannerDraftId: plannerDraftId,
      plannerStatus: plannerStatus,
      plannerTargetExam: plannerTargetExam,
      plannerTargetNet: plannerTargetNet,
      plannerItemCount: plannerItemCount,
      plannerOverviewReason: plannerOverviewReason,
      revisionDueToday: revisionDueToday,
      revisionOverdue: revisionOverdue,
      revisionDueThisWeek: revisionDueThisWeek,
      revisionNextTitle: revisionNextTitle,
      revisionOverviewReason: revisionOverviewReason,
      achievementTotalUnlocked: achievementTotalUnlocked,
      achievementTotalPoints: achievementTotalPoints,
      achievementRecentTitle: achievementRecentTitle,
      achievementRecentReason: achievementRecentReason,
      journeyTodayPct: journeyTodayPct,
      journeyWeekPct: journeyWeekPct,
      journeyMonthPct: journeyMonthPct,
      journeyOverallPct: journeyOverallPct,
      journeyStage: journeyStage,
      journeyOnboardingRequired: journeyOnboardingRequired,
      journeyPrimaryExamType: journeyPrimaryExamType,
      journeyDaysRemaining: journeyDaysRemaining,
      journeyExamDate: journeyExamDate,
      journeyBaselineLevel: journeyBaselineLevel,
      assessmentProgressPct: assessmentProgressPct,
      assessmentMessage: assessmentMessage,
      mySubjectNames: mySubjectNames,
      mySubjectCodes: mySubjectCodes,
      subjectsMostStudied: subjectsMostStudied,
      subjectsWeakest: subjectsWeakest,
      subjectsLongestIdle: subjectsLongestIdle,
      subjectsTodayStudiedCount: subjectsTodayStudiedCount,
      activeExamType: activeExamType,
      primaryExamType: primaryExamType,
      primaryTarget: primaryTarget?.toEntity(),
      activeTarget: activeTarget?.toEntity(),
      nextAction: nextAction?.toEntity(),
      todayContextLines: todayContextLines,
      todayJourneyLine: todayJourneyLine,
      observationState: observationState,
      learningFeed: learningFeed,
      insightCards: insightCards,
      coachToday: coachToday,
      confidenceSummary: confidenceSummary,
      livingPlanSuggestion: livingPlanSuggestion,
    );
  }
}

/// Alignment Sprint-1 — Next Action projection model.
class NextActionModel {
  const NextActionModel({
    required this.title,
    required this.reason,
    required this.actionType,
    required this.deepLinkHint,
    this.subtitle,
    this.ctaLabel = 'Başla',
    this.confidenceTone = 'high',
    this.subjectCode,
    this.topicCode,
    this.purpose,
    this.toolHint,
  });

  final String title;
  final String? subtitle;
  final String reason;
  final String actionType;
  final String deepLinkHint;
  final String ctaLabel;
  final String confidenceTone;
  final String? subjectCode;
  final String? topicCode;
  final String? purpose;
  final String? toolHint;

  factory NextActionModel.fromJson(Map<String, dynamic> json) {
    return NextActionModel(
      title: json['title'] as String? ?? '',
      subtitle: json['subtitle'] as String?,
      reason: json['reason'] as String? ?? '',
      actionType: json['action_type'] as String? ?? 'focus',
      deepLinkHint: json['deep_link_hint'] as String? ?? '/subjects',
      ctaLabel: json['cta_label'] as String? ?? 'Başla',
      confidenceTone: json['confidence_tone'] as String? ?? 'high',
      subjectCode: json['subject_code'] as String?,
      topicCode: json['topic_code'] as String?,
      purpose: json['purpose'] as String?,
      toolHint: json['tool_hint'] as String?,
    );
  }

  NextActionEntity toEntity() => NextActionEntity(
        title: title,
        subtitle: subtitle,
        reason: reason,
        actionType: actionType,
        deepLinkHint: deepLinkHint,
        ctaLabel: ctaLabel,
        confidenceTone: confidenceTone,
        subjectCode: subjectCode,
        topicCode: topicCode,
        purpose: purpose,
        toolHint: toolHint,
      );
}

/// Sprint-3.1.B — exam target summary on dashboard.
class DashboardExamTargetModel {
  const DashboardExamTargetModel({
    required this.examType,
    this.isPrimary = false,
    this.targetNet,
    this.targetScore,
    this.targetRank,
    this.targetUniversity,
    this.targetDepartment,
    this.branch,
    this.examDate,
  });

  final String examType;
  final bool isPrimary;
  final double? targetNet;
  final double? targetScore;
  final int? targetRank;
  final String? targetUniversity;
  final String? targetDepartment;
  final String? branch;
  final DateTime? examDate;

  factory DashboardExamTargetModel.fromJson(Map<String, dynamic> json) {
    return DashboardExamTargetModel(
      examType: json['exam_type'] as String,
      isPrimary: json['is_primary'] as bool? ?? false,
      targetNet: (json['target_net'] as num?)?.toDouble(),
      targetScore: (json['target_score'] as num?)?.toDouble(),
      targetRank: json['target_rank'] as int?,
      targetUniversity: json['target_university'] as String?,
      targetDepartment: json['target_department'] as String?,
      branch: json['branch'] as String?,
      examDate: json['exam_date'] == null
          ? null
          : DateTime.tryParse(json['exam_date'] as String),
    );
  }

  DashboardExamTargetEntity toEntity() => DashboardExamTargetEntity(
        examType: examType,
        isPrimary: isPrimary,
        targetNet: targetNet,
        targetScore: targetScore,
        targetRank: targetRank,
        targetUniversity: targetUniversity,
        targetDepartment: targetDepartment,
        branch: branch,
        examDate: examDate,
      );
}

