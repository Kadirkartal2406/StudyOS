import 'study_plan_status.dart';
import 'study_time.dart';

/// Günlük çalışma planı kalemi — domain katmanında saf Dart nesnesi.
/// Bkz. docs/architecture/database-design.md §1.9, Sprint-1.4 (Meeting-012)
class StudyPlanEntity {
  const StudyPlanEntity({
    required this.id,
    required this.userId,
    required this.title,
    required this.subject,
    required this.targetQuestionCount,
    required this.estimatedMinutes,
    required this.status,
    required this.completedQuestionCount,
    required this.completedMinutes,
    required this.orderIndex,
    required this.studyDate,
    required this.createdAt,
    required this.updatedAt,
    this.topic,
    this.plannedStartTime,
    this.plannedEndTime,
  });

  final String id;
  final String userId;
  final String title;
  final String subject;
  final String? topic;
  final int targetQuestionCount;
  final int estimatedMinutes;
  final StudyTime? plannedStartTime;
  final StudyTime? plannedEndTime;
  final StudyPlanStatus status;
  final int completedQuestionCount;
  final int completedMinutes;
  final int orderIndex;
  final DateTime studyDate;
  final DateTime createdAt;
  final DateTime updatedAt;

  double get progressPercentage {
    if (estimatedMinutes <= 0) return 0.0;
    return (completedMinutes / estimatedMinutes * 100).clamp(0.0, 100.0);
  }

  bool get hasTimeRange => plannedStartTime != null && plannedEndTime != null;

  /// Alignment Sprint-4 — blok etiketi (görev title'ı değil, konu yansıması).
  String get displayLabel {
    final t = topic?.trim();
    if (t != null && t.isNotEmpty) return '$subject · $t';
    return subject.trim().isNotEmpty ? subject : title;
  }

  StudyPlanEntity copyWith({
    StudyPlanStatus? status,
    int? completedQuestionCount,
    int? completedMinutes,
    int? orderIndex,
  }) {
    return StudyPlanEntity(
      id: id,
      userId: userId,
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      plannedStartTime: plannedStartTime,
      plannedEndTime: plannedEndTime,
      status: status ?? this.status,
      completedQuestionCount:
          completedQuestionCount ?? this.completedQuestionCount,
      completedMinutes: completedMinutes ?? this.completedMinutes,
      orderIndex: orderIndex ?? this.orderIndex,
      studyDate: studyDate,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
}
