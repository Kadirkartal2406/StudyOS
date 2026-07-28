/// Revision domain — Sprint-2.8 (S-11 + S-12)
class RevisionScheduleEntity {
  const RevisionScheduleEntity({
    required this.dueAt,
    required this.intervalDays,
    required this.easeFactor,
    required this.repetitionCount,
    this.lapseCount = 0,
    this.lastReviewedAt,
  });

  final DateTime dueAt;
  final int intervalDays;
  final double easeFactor;
  final int repetitionCount;
  final int lapseCount;
  final DateTime? lastReviewedAt;
}

class RevisionItemEntity {
  const RevisionItemEntity({
    required this.id,
    required this.title,
    required this.subject,
    required this.sourceType,
    required this.difficulty,
    required this.reason,
    required this.status,
    this.topic,
    this.note,
    this.sourceId,
    this.schedule,
  });

  final String id;
  final String title;
  final String subject;
  final String? topic;
  final String? note;
  final String sourceType;
  final String? sourceId;
  final int difficulty;
  final String reason;
  final String status;
  final RevisionScheduleEntity? schedule;
}

class RevisionExplainEntity {
  const RevisionExplainEntity({
    required this.revisionId,
    required this.explanation,
    required this.provider,
    required this.reason,
    required this.difficulty,
    this.usedFallback = false,
  });

  final String revisionId;
  final String explanation;
  final String provider;
  final String reason;
  final int difficulty;
  final bool usedFallback;
}

class RevisionStatisticsEntity {
  const RevisionStatisticsEntity({
    this.totalActive = 0,
    this.totalMastered = 0,
    this.dueToday = 0,
    this.overdue = 0,
    this.dueThisWeek = 0,
    this.reviewedToday = 0,
    this.reviewedThisWeek = 0,
    this.averageDifficulty = 0,
    this.averageEase = 0,
  });

  final int totalActive;
  final int totalMastered;
  final int dueToday;
  final int overdue;
  final int dueThisWeek;
  final int reviewedToday;
  final int reviewedThisWeek;
  final double averageDifficulty;
  final double averageEase;
}
