/// Adaptive Planner domain — Sprint-2.7
class PlannerItemEntity {
  const PlannerItemEntity({
    required this.studyDate,
    required this.title,
    required this.subject,
    required this.targetQuestionCount,
    required this.estimatedMinutes,
    required this.reason,
    this.topic,
    this.startTime,
    this.endTime,
    this.resourceIds = const [],
    this.resourceTitles = const [],
  });

  final DateTime studyDate;
  final String title;
  final String subject;
  final String? topic;
  final int targetQuestionCount;
  final int estimatedMinutes;
  final String? startTime;
  final String? endTime;
  final List<String> resourceIds;
  final List<String> resourceTitles;
  final String reason;
}

class PlannerDraftEntity {
  const PlannerDraftEntity({
    required this.id,
    required this.status,
    required this.targetExam,
    required this.targetNet,
    required this.availableDays,
    required this.availableHours,
    required this.items,
    this.summary = const {},
    this.rationale = const {},
    this.overviewReason,
  });

  final String id;
  final String status;
  final String targetExam;
  final double targetNet;
  final List<int> availableDays;
  final double availableHours;
  final List<PlannerItemEntity> items;
  final Map<String, dynamic> summary;
  final Map<String, dynamic> rationale;
  final String? overviewReason;
}

class PlannerExplainEntity {
  const PlannerExplainEntity({
    required this.draftId,
    required this.explanation,
    required this.provider,
    this.usedFallback = false,
  });

  final String draftId;
  final String explanation;
  final String provider;
  final bool usedFallback;
}
