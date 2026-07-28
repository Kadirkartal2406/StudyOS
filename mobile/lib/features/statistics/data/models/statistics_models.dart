import '../../domain/entities/statistics_entities.dart';

class StatisticsOverviewModel {
  const StatisticsOverviewModel({
    required this.totalStudyMinutes,
    required this.todayStudyMinutes,
    required this.todayQuestions,
    required this.weekStudyMinutes,
    required this.monthStudyMinutes,
    required this.totalSessions,
    required this.totalPomodoros,
    required this.completedPlans,
    required this.totalQuestions,
    required this.averageSessionMinutes,
    required this.longestSessionMinutes,
    required this.streakDays,
    this.mostStudiedSubject,
    this.mostStudiedTopic,
    this.mostProductiveWeekdayLabel,
    this.mostProductiveHour,
  });

  final int totalStudyMinutes;
  final int todayStudyMinutes;
  final int todayQuestions;
  final int weekStudyMinutes;
  final int monthStudyMinutes;
  final int totalSessions;
  final int totalPomodoros;
  final int completedPlans;
  final int totalQuestions;
  final double averageSessionMinutes;
  final int longestSessionMinutes;
  final String? mostStudiedSubject;
  final String? mostStudiedTopic;
  final int streakDays;
  final String? mostProductiveWeekdayLabel;
  final int? mostProductiveHour;

  factory StatisticsOverviewModel.fromJson(Map<String, dynamic> json) {
    return StatisticsOverviewModel(
      totalStudyMinutes: json['total_study_minutes'] as int? ?? 0,
      todayStudyMinutes: json['today_study_minutes'] as int? ?? 0,
      todayQuestions: json['today_questions'] as int? ?? 0,
      weekStudyMinutes: json['week_study_minutes'] as int? ?? 0,
      monthStudyMinutes: json['month_study_minutes'] as int? ?? 0,
      totalSessions: json['total_sessions'] as int? ?? 0,
      totalPomodoros: json['total_pomodoros'] as int? ?? 0,
      completedPlans: json['completed_plans'] as int? ?? 0,
      totalQuestions: json['total_questions'] as int? ?? 0,
      averageSessionMinutes:
          (json['average_session_minutes'] as num?)?.toDouble() ?? 0,
      longestSessionMinutes: json['longest_session_minutes'] as int? ?? 0,
      mostStudiedSubject: json['most_studied_subject'] as String?,
      mostStudiedTopic: json['most_studied_topic'] as String?,
      streakDays: json['streak_days'] as int? ?? 0,
      mostProductiveWeekdayLabel:
          json['most_productive_weekday_label'] as String?,
      mostProductiveHour: json['most_productive_hour'] as int?,
    );
  }

  StatisticsOverviewEntity toEntity() => StatisticsOverviewEntity(
        totalStudyMinutes: totalStudyMinutes,
        todayStudyMinutes: todayStudyMinutes,
        todayQuestions: todayQuestions,
        weekStudyMinutes: weekStudyMinutes,
        monthStudyMinutes: monthStudyMinutes,
        totalSessions: totalSessions,
        totalPomodoros: totalPomodoros,
        completedPlans: completedPlans,
        totalQuestions: totalQuestions,
        averageSessionMinutes: averageSessionMinutes,
        longestSessionMinutes: longestSessionMinutes,
        mostStudiedSubject: mostStudiedSubject,
        mostStudiedTopic: mostStudiedTopic,
        streakDays: streakDays,
        mostProductiveWeekdayLabel: mostProductiveWeekdayLabel,
        mostProductiveHour: mostProductiveHour,
      );
}

class TimeBucketModel {
  const TimeBucketModel({
    required this.label,
    required this.studyMinutes,
    required this.sessionCount,
    required this.questionCount,
  });

  final String label;
  final int studyMinutes;
  final int sessionCount;
  final int questionCount;

  factory TimeBucketModel.fromJson(Map<String, dynamic> json) {
    return TimeBucketModel(
      label: json['label'] as String? ?? '',
      studyMinutes: json['study_minutes'] as int? ?? 0,
      sessionCount: json['session_count'] as int? ?? 0,
      questionCount: json['question_count'] as int? ?? 0,
    );
  }

  TimeBucketEntity toEntity() => TimeBucketEntity(
        label: label,
        studyMinutes: studyMinutes,
        sessionCount: sessionCount,
        questionCount: questionCount,
      );
}

class DistributionItemModel {
  const DistributionItemModel({
    required this.name,
    required this.studyMinutes,
    required this.sessionCount,
    required this.questionCount,
    required this.percentage,
  });

  final String name;
  final int studyMinutes;
  final int sessionCount;
  final int questionCount;
  final double percentage;

  factory DistributionItemModel.fromJson(Map<String, dynamic> json) {
    return DistributionItemModel(
      name: json['name'] as String? ?? '',
      studyMinutes: json['study_minutes'] as int? ?? 0,
      sessionCount: json['session_count'] as int? ?? 0,
      questionCount: json['question_count'] as int? ?? 0,
      percentage: (json['percentage'] as num?)?.toDouble() ?? 0,
    );
  }

  DistributionItemEntity toEntity() => DistributionItemEntity(
        name: name,
        studyMinutes: studyMinutes,
        sessionCount: sessionCount,
        questionCount: questionCount,
        percentage: percentage,
      );
}

class StatisticsPeriodModel {
  const StatisticsPeriodModel({
    required this.studyMinutes,
    required this.sessionCount,
    required this.questionCount,
    required this.completedPlans,
    required this.buckets,
  });

  final int studyMinutes;
  final int sessionCount;
  final int questionCount;
  final int completedPlans;
  final List<TimeBucketModel> buckets;

  factory StatisticsPeriodModel.fromJson(Map<String, dynamic> json) {
    final raw = json['buckets'] as List<dynamic>? ?? [];
    return StatisticsPeriodModel(
      studyMinutes: json['study_minutes'] as int? ?? 0,
      sessionCount: json['session_count'] as int? ?? 0,
      questionCount: json['question_count'] as int? ?? 0,
      completedPlans: json['completed_plans'] as int? ?? 0,
      buckets: raw
          .map((e) => TimeBucketModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  StatisticsPeriodEntity toEntity() => StatisticsPeriodEntity(
        studyMinutes: studyMinutes,
        sessionCount: sessionCount,
        questionCount: questionCount,
        completedPlans: completedPlans,
        buckets: buckets.map((b) => b.toEntity()).toList(),
      );
}

class StatisticsDailyModel {
  const StatisticsDailyModel({
    required this.studyMinutes,
    required this.sessionCount,
    required this.questionCount,
    required this.completedPlans,
    required this.buckets,
  });

  final int studyMinutes;
  final int sessionCount;
  final int questionCount;
  final int completedPlans;
  final List<TimeBucketModel> buckets;

  factory StatisticsDailyModel.fromJson(Map<String, dynamic> json) {
    final raw = json['buckets'] as List<dynamic>? ?? [];
    return StatisticsDailyModel(
      studyMinutes: json['study_minutes'] as int? ?? 0,
      sessionCount: json['session_count'] as int? ?? 0,
      questionCount: json['question_count'] as int? ?? 0,
      completedPlans: json['completed_plans'] as int? ?? 0,
      buckets: raw
          .map((e) => TimeBucketModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  StatisticsDailyEntity toEntity() => StatisticsDailyEntity(
        studyMinutes: studyMinutes,
        sessionCount: sessionCount,
        questionCount: questionCount,
        completedPlans: completedPlans,
        buckets: buckets.map((b) => b.toEntity()).toList(),
      );
}

class StatisticsDistributionModel {
  const StatisticsDistributionModel({
    required this.totalMinutes,
    required this.items,
  });

  final int totalMinutes;
  final List<DistributionItemModel> items;

  factory StatisticsDistributionModel.fromJson(Map<String, dynamic> json) {
    final raw = json['items'] as List<dynamic>? ?? [];
    return StatisticsDistributionModel(
      totalMinutes: json['total_minutes'] as int? ?? 0,
      items: raw
          .map(
            (e) => DistributionItemModel.fromJson(e as Map<String, dynamic>),
          )
          .toList(),
    );
  }

  StatisticsDistributionEntity toEntity() => StatisticsDistributionEntity(
        totalMinutes: totalMinutes,
        items: items.map((i) => i.toEntity()).toList(),
      );
}

class HeatmapDayModel {
  const HeatmapDayModel({
    required this.date,
    required this.studyMinutes,
    required this.sessionCount,
  });

  final DateTime date;
  final int studyMinutes;
  final int sessionCount;

  factory HeatmapDayModel.fromJson(Map<String, dynamic> json) {
    return HeatmapDayModel(
      date: DateTime.parse(json['date'] as String),
      studyMinutes: json['study_minutes'] as int? ?? 0,
      sessionCount: json['session_count'] as int? ?? 0,
    );
  }

  HeatmapDayEntity toEntity() => HeatmapDayEntity(
        date: date,
        studyMinutes: studyMinutes,
        sessionCount: sessionCount,
      );
}

class StatisticsHeatmapModel {
  const StatisticsHeatmapModel({required this.days});

  final List<HeatmapDayModel> days;

  factory StatisticsHeatmapModel.fromJson(Map<String, dynamic> json) {
    final raw = json['days'] as List<dynamic>? ?? [];
    return StatisticsHeatmapModel(
      days: raw
          .map((e) => HeatmapDayModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  StatisticsHeatmapEntity toEntity() => StatisticsHeatmapEntity(
        days: days.map((d) => d.toEntity()).toList(),
      );
}
