/// İstatistik domain entity'leri — Sprint-1.6
class StatisticsOverviewEntity {
  const StatisticsOverviewEntity({
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
}

class TimeBucketEntity {
  const TimeBucketEntity({
    required this.label,
    required this.studyMinutes,
    required this.sessionCount,
    required this.questionCount,
  });

  final String label;
  final int studyMinutes;
  final int sessionCount;
  final int questionCount;
}

class DistributionItemEntity {
  const DistributionItemEntity({
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
}

class StatisticsPeriodEntity {
  const StatisticsPeriodEntity({
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
  final List<TimeBucketEntity> buckets;
}

class StatisticsDailyEntity {
  const StatisticsDailyEntity({
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
  final List<TimeBucketEntity> buckets;
}

class StatisticsDistributionEntity {
  const StatisticsDistributionEntity({
    required this.totalMinutes,
    required this.items,
  });

  final int totalMinutes;
  final List<DistributionItemEntity> items;
}

class HeatmapDayEntity {
  const HeatmapDayEntity({
    required this.date,
    required this.studyMinutes,
    required this.sessionCount,
  });

  final DateTime date;
  final int studyMinutes;
  final int sessionCount;
}

class StatisticsHeatmapEntity {
  const StatisticsHeatmapEntity({required this.days});

  final List<HeatmapDayEntity> days;
}
