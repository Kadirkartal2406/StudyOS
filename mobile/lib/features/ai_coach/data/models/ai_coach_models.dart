import '../../domain/entities/ai_coach_entities.dart';

class AiRecommendationModel {
  const AiRecommendationModel({
    required this.code,
    required this.message,
    required this.priority,
    this.category = 'general',
  });

  final String code;
  final String message;
  final int priority;
  final String category;

  factory AiRecommendationModel.fromJson(Map<String, dynamic> json) {
    return AiRecommendationModel(
      code: json['code'] as String,
      message: json['message'] as String,
      priority: json['priority'] as int? ?? 50,
      category: json['category'] as String? ?? 'general',
    );
  }

  AiRecommendationEntity toEntity() => AiRecommendationEntity(
        code: code,
        message: message,
        priority: priority,
        category: category,
      );
}

class AiInsightMetricModel {
  const AiInsightMetricModel({
    required this.key,
    required this.label,
    this.value,
    this.unit,
  });

  final String key;
  final String label;
  final Object? value;
  final String? unit;

  factory AiInsightMetricModel.fromJson(Map<String, dynamic> json) {
    return AiInsightMetricModel(
      key: json['key'] as String,
      label: json['label'] as String,
      value: json['value'],
      unit: json['unit'] as String?,
    );
  }

  AiInsightMetricEntity toEntity() => AiInsightMetricEntity(
        key: key,
        label: label,
        value: value,
        unit: unit,
      );
}

class AiOverviewModel {
  const AiOverviewModel({
    required this.hasEnoughData,
    this.streakDays = 0,
    this.averageDailyMinutes = 0,
    this.averageDailyQuestions = 0,
    this.mostStudiedSubject,
    this.leastStudiedSubject,
    this.mostQuestionsSubject,
    this.correctRate = 0,
    this.pomodoroCompletionRate = 0,
    this.mostProductiveHour,
    this.leastProductiveHour,
    this.idleDaysLast14 = 0,
    this.topRecommendation,
    this.recommendationsCount = 0,
  });

  final bool hasEnoughData;
  final int streakDays;
  final double averageDailyMinutes;
  final double averageDailyQuestions;
  final String? mostStudiedSubject;
  final String? leastStudiedSubject;
  final String? mostQuestionsSubject;
  final double correctRate;
  final double pomodoroCompletionRate;
  final int? mostProductiveHour;
  final int? leastProductiveHour;
  final int idleDaysLast14;
  final AiRecommendationModel? topRecommendation;
  final int recommendationsCount;

  factory AiOverviewModel.fromJson(Map<String, dynamic> json) {
    final top = json['top_recommendation'] as Map<String, dynamic>?;
    return AiOverviewModel(
      hasEnoughData: json['has_enough_data'] as bool? ?? false,
      streakDays: json['streak_days'] as int? ?? 0,
      averageDailyMinutes:
          (json['average_daily_minutes'] as num?)?.toDouble() ?? 0,
      averageDailyQuestions:
          (json['average_daily_questions'] as num?)?.toDouble() ?? 0,
      mostStudiedSubject: json['most_studied_subject'] as String?,
      leastStudiedSubject: json['least_studied_subject'] as String?,
      mostQuestionsSubject: json['most_questions_subject'] as String?,
      correctRate: (json['correct_rate'] as num?)?.toDouble() ?? 0,
      pomodoroCompletionRate:
          (json['pomodoro_completion_rate'] as num?)?.toDouble() ?? 0,
      mostProductiveHour: json['most_productive_hour'] as int?,
      leastProductiveHour: json['least_productive_hour'] as int?,
      idleDaysLast14: json['idle_days_last_14'] as int? ?? 0,
      topRecommendation:
          top == null ? null : AiRecommendationModel.fromJson(top),
      recommendationsCount: json['recommendations_count'] as int? ?? 0,
    );
  }

  AiOverviewEntity toEntity() => AiOverviewEntity(
        hasEnoughData: hasEnoughData,
        streakDays: streakDays,
        averageDailyMinutes: averageDailyMinutes,
        averageDailyQuestions: averageDailyQuestions,
        mostStudiedSubject: mostStudiedSubject,
        leastStudiedSubject: leastStudiedSubject,
        mostQuestionsSubject: mostQuestionsSubject,
        correctRate: correctRate,
        pomodoroCompletionRate: pomodoroCompletionRate,
        mostProductiveHour: mostProductiveHour,
        leastProductiveHour: leastProductiveHour,
        idleDaysLast14: idleDaysLast14,
        topRecommendation: topRecommendation?.toEntity(),
        recommendationsCount: recommendationsCount,
      );
}

class AiTrendPointModel {
  const AiTrendPointModel({
    required this.label,
    this.studyMinutes = 0,
    this.questionCount = 0,
  });

  final String label;
  final int studyMinutes;
  final int questionCount;

  factory AiTrendPointModel.fromJson(Map<String, dynamic> json) {
    return AiTrendPointModel(
      label: json['label'] as String,
      studyMinutes: json['study_minutes'] as int? ?? 0,
      questionCount: json['question_count'] as int? ?? 0,
    );
  }

  AiTrendPointEntity toEntity() => AiTrendPointEntity(
        label: label,
        studyMinutes: studyMinutes,
        questionCount: questionCount,
      );
}

class AiTrendsModel {
  const AiTrendsModel({
    this.weeklyStudyMinutes = 0,
    this.previousWeekStudyMinutes = 0,
    this.studyMinutesDeltaPct,
    this.weeklyQuestions = 0,
    this.previousWeekQuestions = 0,
    this.questionsDeltaPct,
    this.monthlyStudyMinutes = 0,
    this.previousMonthStudyMinutes = 0,
    this.dailySeries = const [],
  });

  final int weeklyStudyMinutes;
  final int previousWeekStudyMinutes;
  final double? studyMinutesDeltaPct;
  final int weeklyQuestions;
  final int previousWeekQuestions;
  final double? questionsDeltaPct;
  final int monthlyStudyMinutes;
  final int previousMonthStudyMinutes;
  final List<AiTrendPointModel> dailySeries;

  factory AiTrendsModel.fromJson(Map<String, dynamic> json) {
    final series = json['daily_series'] as List<dynamic>? ?? [];
    return AiTrendsModel(
      weeklyStudyMinutes: json['weekly_study_minutes'] as int? ?? 0,
      previousWeekStudyMinutes:
          json['previous_week_study_minutes'] as int? ?? 0,
      studyMinutesDeltaPct:
          (json['study_minutes_delta_pct'] as num?)?.toDouble(),
      weeklyQuestions: json['weekly_questions'] as int? ?? 0,
      previousWeekQuestions: json['previous_week_questions'] as int? ?? 0,
      questionsDeltaPct: (json['questions_delta_pct'] as num?)?.toDouble(),
      monthlyStudyMinutes: json['monthly_study_minutes'] as int? ?? 0,
      previousMonthStudyMinutes:
          json['previous_month_study_minutes'] as int? ?? 0,
      dailySeries: series
          .map((e) => AiTrendPointModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  AiTrendsEntity toEntity() => AiTrendsEntity(
        weeklyStudyMinutes: weeklyStudyMinutes,
        previousWeekStudyMinutes: previousWeekStudyMinutes,
        studyMinutesDeltaPct: studyMinutesDeltaPct,
        weeklyQuestions: weeklyQuestions,
        previousWeekQuestions: previousWeekQuestions,
        questionsDeltaPct: questionsDeltaPct,
        monthlyStudyMinutes: monthlyStudyMinutes,
        previousMonthStudyMinutes: previousMonthStudyMinutes,
        dailySeries: dailySeries.map((e) => e.toEntity()).toList(),
      );
}

class AiPerformanceModel {
  const AiPerformanceModel({
    this.correctRate = 0,
    this.wrongRate = 0,
    this.totalNet = 0,
    this.totalQuestions = 0,
    this.subjectsByAccuracy = const [],
    this.subjectsByQuestions = const [],
    this.pomodoroCompletionRate = 0,
    this.totalPomodoros = 0,
  });

  final double correctRate;
  final double wrongRate;
  final double totalNet;
  final int totalQuestions;
  final List<AiInsightMetricModel> subjectsByAccuracy;
  final List<AiInsightMetricModel> subjectsByQuestions;
  final double pomodoroCompletionRate;
  final int totalPomodoros;

  factory AiPerformanceModel.fromJson(Map<String, dynamic> json) {
    final byAcc = json['subjects_by_accuracy'] as List<dynamic>? ?? [];
    final byQ = json['subjects_by_questions'] as List<dynamic>? ?? [];
    return AiPerformanceModel(
      correctRate: (json['correct_rate'] as num?)?.toDouble() ?? 0,
      wrongRate: (json['wrong_rate'] as num?)?.toDouble() ?? 0,
      totalNet: (json['total_net'] as num?)?.toDouble() ?? 0,
      totalQuestions: json['total_questions'] as int? ?? 0,
      subjectsByAccuracy: byAcc
          .map((e) => AiInsightMetricModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      subjectsByQuestions: byQ
          .map((e) => AiInsightMetricModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      pomodoroCompletionRate:
          (json['pomodoro_completion_rate'] as num?)?.toDouble() ?? 0,
      totalPomodoros: json['total_pomodoros'] as int? ?? 0,
    );
  }

  AiPerformanceEntity toEntity() => AiPerformanceEntity(
        correctRate: correctRate,
        wrongRate: wrongRate,
        totalNet: totalNet,
        totalQuestions: totalQuestions,
        subjectsByAccuracy:
            subjectsByAccuracy.map((e) => e.toEntity()).toList(),
        subjectsByQuestions:
            subjectsByQuestions.map((e) => e.toEntity()).toList(),
        pomodoroCompletionRate: pomodoroCompletionRate,
        totalPomodoros: totalPomodoros,
      );
}

class AiProductivityModel {
  const AiProductivityModel({
    this.mostProductiveHour,
    this.leastProductiveHour,
    this.mostProductiveWeekdayLabel,
    this.hourMinutes = const [],
    this.weekdayMinutes = const [],
    this.streakDays = 0,
    this.idleDaysLast14 = 0,
    this.averageDailyMinutes = 0,
    this.averageDailyQuestions = 0,
  });

  final int? mostProductiveHour;
  final int? leastProductiveHour;
  final String? mostProductiveWeekdayLabel;
  final List<int> hourMinutes;
  final List<int> weekdayMinutes;
  final int streakDays;
  final int idleDaysLast14;
  final double averageDailyMinutes;
  final double averageDailyQuestions;

  factory AiProductivityModel.fromJson(Map<String, dynamic> json) {
    final hours = json['hour_minutes'] as List<dynamic>? ?? [];
    final weekdays = json['weekday_minutes'] as List<dynamic>? ?? [];
    return AiProductivityModel(
      mostProductiveHour: json['most_productive_hour'] as int?,
      leastProductiveHour: json['least_productive_hour'] as int?,
      mostProductiveWeekdayLabel:
          json['most_productive_weekday_label'] as String?,
      hourMinutes: hours.map((e) => (e as num).toInt()).toList(),
      weekdayMinutes: weekdays.map((e) => (e as num).toInt()).toList(),
      streakDays: json['streak_days'] as int? ?? 0,
      idleDaysLast14: json['idle_days_last_14'] as int? ?? 0,
      averageDailyMinutes:
          (json['average_daily_minutes'] as num?)?.toDouble() ?? 0,
      averageDailyQuestions:
          (json['average_daily_questions'] as num?)?.toDouble() ?? 0,
    );
  }

  AiProductivityEntity toEntity() => AiProductivityEntity(
        mostProductiveHour: mostProductiveHour,
        leastProductiveHour: leastProductiveHour,
        mostProductiveWeekdayLabel: mostProductiveWeekdayLabel,
        hourMinutes: hourMinutes,
        weekdayMinutes: weekdayMinutes,
        streakDays: streakDays,
        idleDaysLast14: idleDaysLast14,
        averageDailyMinutes: averageDailyMinutes,
        averageDailyQuestions: averageDailyQuestions,
      );
}
