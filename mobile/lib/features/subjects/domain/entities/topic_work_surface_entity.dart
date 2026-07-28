/// Alignment Sprint-3 — Topic Work Surface domain entities.
/// Sprint 15 — Intelligence projections (read-only).

class TopicLearningStateEntity {
  const TopicLearningStateEntity({
    required this.subjectCode,
    required this.topicCode,
    required this.topicName,
    this.subjectName,
    this.summaryLine,
    this.revisionDue = false,
    this.studyMinutes = 0,
    this.sessionCount = 0,
    this.correctCount = 0,
    this.wrongCount = 0,
    this.blankCount = 0,
    this.questionCount = 0,
    this.accuracyPct = 0,
  });

  final String subjectCode;
  final String topicCode;
  final String topicName;
  final String? subjectName;
  final String? summaryLine;
  final bool revisionDue;
  final int studyMinutes;
  final int sessionCount;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final int questionCount;
  final double accuracyPct;
}

class TopicSecondaryToolEntity {
  const TopicSecondaryToolEntity({
    required this.id,
    required this.label,
    required this.deepLinkHint,
  });

  final String id;
  final String label;
  final String deepLinkHint;
}

class TopicPrimaryActionEntity {
  const TopicPrimaryActionEntity({
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

class TopicIntelligenceEntity {
  const TopicIntelligenceEntity({
    required this.topicName,
    required this.headline,
    this.stars = 0,
    this.lastStudiedLabel,
    this.lastQuizLabel,
    this.confidenceLabel = 'Bilinmiyor',
    this.confidenceLevel = 'unknown',
    this.weakSpot,
    this.suggestion,
  });

  final String topicName;
  final String headline;
  final int stars;
  final String? lastStudiedLabel;
  final String? lastQuizLabel;
  final String confidenceLabel;
  final String confidenceLevel;
  final String? weakSpot;
  final String? suggestion;
}

class TimelineEventEntity {
  const TimelineEventEntity({
    required this.id,
    required this.kind,
    required this.title,
    required this.relativeLabel,
    this.subtitle,
    this.deepLinkHint,
  });

  final String id;
  final String kind;
  final String title;
  final String? subtitle;
  final String relativeLabel;
  final String? deepLinkHint;
}

class InsightCardEntity {
  const InsightCardEntity({
    required this.id,
    required this.code,
    required this.message,
    this.tone = 'neutral',
    this.subjectCode,
    this.topicCode,
    this.topicName,
    this.deepLinkHint,
  });

  final String id;
  final String code;
  final String message;
  final String tone;
  final String? subjectCode;
  final String? topicCode;
  final String? topicName;
  final String? deepLinkHint;
}

class QuizHistoryItemEntity {
  const QuizHistoryItemEntity({
    required this.id,
    required this.questionCount,
    required this.status,
    required this.relativeLabel,
    this.accuracyPct,
    this.correctCount,
    this.difficulty = 'medium',
  });

  final String id;
  final int questionCount;
  final double? accuracyPct;
  final int? correctCount;
  final String status;
  final String relativeLabel;
  final String difficulty;
}

class ResourceIntelligenceEntity {
  const ResourceIntelligenceEntity({
    required this.id,
    required this.title,
    required this.intelligenceLabel,
    this.resourceType = 'other',
    this.status = 'not_started',
    this.url,
    this.knowledgeHealth,
    this.chunkCount = 0,
    this.citationCount = 0,
    this.quizGeneratedCount = 0,
    this.usedByAi = false,
  });

  final String id;
  final String title;
  final String intelligenceLabel;
  final String resourceType;
  final String status;
  final String? url;
  final String? knowledgeHealth;
  final int chunkCount;
  final int citationCount;
  final int quizGeneratedCount;
  final bool usedByAi;
}

class TopicWorkSurfaceEntity {
  const TopicWorkSurfaceEntity({
    required this.learningState,
    required this.primaryAction,
    this.secondaryTools = const [],
    this.intelligence,
    this.timeline = const [],
    this.insights = const [],
    this.quizHistory = const [],
    this.resources = const [],
    this.coachHeadline,
    this.coachBody,
    this.coachCtaLabel,
    this.coachDeepLinkHint,
  });

  final TopicLearningStateEntity learningState;
  final TopicPrimaryActionEntity primaryAction;
  final List<TopicSecondaryToolEntity> secondaryTools;
  final TopicIntelligenceEntity? intelligence;
  final List<TimelineEventEntity> timeline;
  final List<InsightCardEntity> insights;
  final List<QuizHistoryItemEntity> quizHistory;
  final List<ResourceIntelligenceEntity> resources;
  final String? coachHeadline;
  final String? coachBody;
  final String? coachCtaLabel;
  final String? coachDeepLinkHint;
}
