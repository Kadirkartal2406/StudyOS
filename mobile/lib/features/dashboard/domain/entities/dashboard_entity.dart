import 'activity_entity.dart';

/// Dashboard'daki haftalık hedef özeti (Sprint-2.1 / 3.0.2).
class WeeklyGoalSummaryEntity {
  const WeeklyGoalSummaryEntity({
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
}

/// Sprint-3.1.B — Hero Primary/Active hedef özeti.
class DashboardExamTargetEntity {
  const DashboardExamTargetEntity({
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
}

/// Alignment Sprint-1 — Decision Engine Projection (tek Primary Action).
class NextActionEntity {
  const NextActionEntity({
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
}

/// Ana ekran (Dashboard) özet verisi entity'si.
class DashboardEntity {
  const DashboardEntity({
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
  final List<ActivityEntity> recentActivities;
  final String? todayAiRecommendation;
  final String? todayAiRecommendationCode;
  final String? todayAiRecommendationReason;
  final List<WeeklyGoalSummaryEntity> weeklyGoals;
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
  /// Sprint 18 — Assessment Progress
  final double assessmentProgressPct;
  final String? assessmentMessage;
  final List<String> mySubjectNames;
  /// Sprint-3.1.C — hub deep-link identity (parallel to names).
  final List<String> mySubjectCodes;
  final String? subjectsMostStudied;
  final String? subjectsWeakest;
  final String? subjectsLongestIdle;
  final int subjectsTodayStudiedCount;
  final String? activeExamType;
  final String? primaryExamType;
  final DashboardExamTargetEntity? primaryTarget;
  final DashboardExamTargetEntity? activeTarget;
  /// Alignment Sprint-1 — Decision Projection (tek Primary Action).
  final NextActionEntity? nextAction;
  final List<String> todayContextLines;
  final String? todayJourneyLine;

  /// Sprint-8 — Today Engine observation state.
  /// Values: "observing" | "calibrating" | "full"
  final String observationState;

  /// Sprint 15 — Personalized feed + insights (Decision değil).
  final List<FeedCardEntity> learningFeed;
  final List<InsightCardEntity> insightCards;

  /// Sprint 20 — Adaptive Coach (Experience).
  final CoachTodayEntity? coachToday;
}

/// Sprint 20 — Today Coach mesajı.
class CoachTodayEntity {
  const CoachTodayEntity({
    required this.headline,
    required this.body,
    this.focusTopic,
    this.suggestedMinutes,
    this.habitHint,
    this.deepLinkHint,
    this.ctaLabel = 'Başla',
    this.winTitle,
    this.winMessage,
    this.reasons = const [],
  });

  final String headline;
  final String body;
  final String? focusTopic;
  final int? suggestedMinutes;
  final String? habitHint;
  final String? deepLinkHint;
  final String ctaLabel;
  final String? winTitle;
  final String? winMessage;
  final List<String> reasons;
}

/// Sprint 15 — Dashboard feed kartı.
class FeedCardEntity {
  const FeedCardEntity({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.kind,
    this.deepLinkHint,
    this.tone = 'neutral',
    this.subjectCode,
    this.topicCode,
  });

  final String id;
  final String title;
  final String subtitle;
  final String kind;
  final String? deepLinkHint;
  final String tone;
  final String? subjectCode;
  final String? topicCode;
}

/// Sprint 15 — Insight kartı.
class InsightCardEntity {
  const InsightCardEntity({
    required this.id,
    required this.code,
    required this.message,
    this.tone = 'neutral',
    this.deepLinkHint,
  });

  final String id;
  final String code;
  final String message;
  final String tone;
  final String? deepLinkHint;
}
