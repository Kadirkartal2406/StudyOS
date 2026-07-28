/// Sprint-3.0 — Learning Profile entities
class LearningProfileEntity {
  const LearningProfileEntity({
    required this.userId,
    required this.journeyStage,
    required this.onboardingCompleted,
    required this.onboardingSkipped,
    required this.onboardingRequired,
    required this.dailyStudyMinutes,
    required this.availableDays,
    required this.availableHours,
    required this.baselineLevel,
    this.baselineReason,
    this.examTargets = const [],
    this.subjects = const [],
    this.primaryExamType,
    this.activeExamType,
  });

  final String userId;
  final String journeyStage;
  final bool onboardingCompleted;
  final bool onboardingSkipped;
  final bool onboardingRequired;
  final int dailyStudyMinutes;
  final List<int> availableDays;
  final double availableHours;
  final String baselineLevel;
  final String? baselineReason;
  final List<ExamTargetEntity> examTargets;
  final List<UserSubjectEntity> subjects;
  /// Sprint-3.1.A — backend SSOT fields
  final String? primaryExamType;
  final String? activeExamType;
}

class ExamTargetEntity {
  const ExamTargetEntity({
    required this.id,
    required this.examType,
    required this.isPrimary,
    this.targetNet,
    this.targetScore,
    this.targetRank,
    this.targetUniversity,
    this.targetDepartment,
    this.branch,
    this.examDate,
  });

  final String id;
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

class UserSubjectEntity {
  const UserSubjectEntity({
    required this.subjectCode,
    required this.subjectName,
    required this.isActive,
    this.id,
    this.section,
    this.totalQuestions = 0,
    this.studyMinutes = 0,
    this.accuracy = 0,
    this.lastStudiedAt,
    this.lastRevisionAt,
    this.progressPct = 0,
  });

  final String? id;
  final String subjectCode;
  final String subjectName;
  final bool isActive;
  final String? section;
  final int totalQuestions;
  final int studyMinutes;
  final double accuracy;
  final DateTime? lastStudiedAt;
  final DateTime? lastRevisionAt;
  final double progressPct;
}

class OnboardingStatusEntity {
  const OnboardingStatusEntity({
    required this.onboardingRequired,
    required this.onboardingCompleted,
    required this.onboardingSkipped,
    required this.journeyStage,
    this.canSkip = false,
  });

  final bool onboardingRequired;
  final bool onboardingCompleted;
  final bool onboardingSkipped;
  final String journeyStage;
  final bool canSkip;
}
