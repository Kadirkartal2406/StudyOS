/// AI Coach domain entities — Sprint-2.0 (rule-based insights, no LLM).

class AiRecommendationEntity {
  const AiRecommendationEntity({
    required this.code,
    required this.message,
    required this.priority,
    this.category = 'general',
  });

  final String code;
  final String message;
  final int priority;
  final String category;
}

class AiInsightMetricEntity {
  const AiInsightMetricEntity({
    required this.key,
    required this.label,
    this.value,
    this.unit,
  });

  final String key;
  final String label;
  final Object? value;
  final String? unit;
}

class AiOverviewEntity {
  const AiOverviewEntity({
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
  final AiRecommendationEntity? topRecommendation;
  final int recommendationsCount;
}

class AiTrendPointEntity {
  const AiTrendPointEntity({
    required this.label,
    this.studyMinutes = 0,
    this.questionCount = 0,
  });

  final String label;
  final int studyMinutes;
  final int questionCount;
}

class AiTrendsEntity {
  const AiTrendsEntity({
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
  final List<AiTrendPointEntity> dailySeries;
}

class AiPerformanceEntity {
  const AiPerformanceEntity({
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
  final List<AiInsightMetricEntity> subjectsByAccuracy;
  final List<AiInsightMetricEntity> subjectsByQuestions;
  final double pomodoroCompletionRate;
  final int totalPomodoros;
}

class AiProductivityEntity {
  const AiProductivityEntity({
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
}
