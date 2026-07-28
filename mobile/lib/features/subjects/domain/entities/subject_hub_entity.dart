/// Sprint-3.1.C — Subject Hub sectioned entity (subject_code identity).
class SubjectHubEntity {
  const SubjectHubEntity({
    required this.subject,
    required this.progress,
    required this.today,
    required this.revision,
    required this.plans,
    required this.examSummary,
    required this.resources,
    required this.flashcards,
    required this.topics,
    required this.ai,
    this.activeExamType,
    this.primaryExamType,
  });

  final SubjectHubIdentity subject;
  final SubjectHubProgress progress;
  final SubjectHubToday today;
  final SubjectHubRevision revision;
  final SubjectHubPlans plans;
  final SubjectHubExamSummary examSummary;
  final SubjectHubResources resources;
  final SubjectHubFlashcards flashcards;
  final SubjectHubTopics topics;
  final SubjectHubAi ai;
  final String? activeExamType;
  final String? primaryExamType;
}

class SubjectHubIdentity {
  const SubjectHubIdentity({
    required this.subjectCode,
    required this.subjectName,
    this.section,
    this.examTypes = const [],
    this.isActive = true,
    this.source = 'onboarding',
  });

  final String subjectCode;
  final String subjectName;
  final String? section;
  final List<String> examTypes;
  final bool isActive;
  final String source;
}

class SubjectHubProgress {
  const SubjectHubProgress({
    this.progressPct = 0,
    this.accuracy = 0,
    this.totalQuestions = 0,
    this.studyMinutes = 0,
    this.lastStudiedAt,
    this.lastRevisionAt,
  });

  final double progressPct;
  final double accuracy;
  final int totalQuestions;
  final int studyMinutes;
  final DateTime? lastStudiedAt;
  final DateTime? lastRevisionAt;
}

class SubjectHubToday {
  const SubjectHubToday({
    this.studyMinutes = 0,
    this.questionsSolved = 0,
    this.planCount = 0,
    this.completedPlanCount = 0,
  });

  final int studyMinutes;
  final int questionsSolved;
  final int planCount;
  final int completedPlanCount;
}

class SubjectHubRevision {
  const SubjectHubRevision({
    this.dueToday = 0,
    this.overdue = 0,
    this.dueThisWeek = 0,
    this.nextTitle,
    this.overviewReason,
    this.available = true,
  });

  final int dueToday;
  final int overdue;
  final int dueThisWeek;
  final String? nextTitle;
  final String? overviewReason;
  final bool available;
}

class SubjectHubPlans {
  const SubjectHubPlans({
    this.todayCount = 0,
    this.completedCount = 0,
    this.nextTitle,
    this.overviewReason,
    this.available = true,
  });

  final int todayCount;
  final int completedCount;
  final String? nextTitle;
  final String? overviewReason;
  final bool available;
}

class SubjectHubExamSummary {
  const SubjectHubExamSummary({
    this.averageNet,
    this.examCount = 0,
    this.lastNet,
    this.available = false,
    this.placeholder = true,
  });

  final double? averageNet;
  final int examCount;
  final double? lastNet;
  final bool available;
  final bool placeholder;
}

class SubjectHubResources {
  const SubjectHubResources({
    this.count = 0,
    this.recentTitles = const [],
    this.available = false,
    this.placeholder = true,
  });

  final int count;
  final List<String> recentTitles;
  final bool available;
  final bool placeholder;
}

class SubjectHubFlashcards {
  const SubjectHubFlashcards({
    this.enabled = false,
    this.placeholder = true,
    this.message = 'Flashcards yakında',
  });

  final bool enabled;
  final bool placeholder;
  final String message;
}

/// Sprint-3.2.A — Topic Catalog item (topic_code identity).
class TopicCatalogItem {
  const TopicCatalogItem({
    required this.topicCode,
    required this.topicName,
    required this.subjectCode,
    this.sortOrder = 0,
    this.difficulty,
    this.isActive = true,
  });

  final String topicCode;
  final String topicName;
  final String subjectCode;
  final int sortOrder;
  final int? difficulty;
  final bool isActive;
}

class SubjectHubTopics {
  const SubjectHubTopics({
    this.items = const [],
    this.count = 0,
    this.available = true,
  });

  final List<TopicCatalogItem> items;
  final int count;
  final bool available;
}

class SubjectHubAi {
  const SubjectHubAi({
    this.recommendation,
    this.reason,
    this.code,
    this.explainAvailable = false,
    this.explainPlaceholder = 'Explain yakında (Sprint-3.1.D)',
  });

  final String? recommendation;
  final String? reason;
  final String? code;
  final bool explainAvailable;
  final String explainPlaceholder;
}
