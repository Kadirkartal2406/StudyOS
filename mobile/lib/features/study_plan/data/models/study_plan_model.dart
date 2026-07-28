import '../../domain/entities/study_plan_entity.dart';
import '../../domain/entities/study_plan_status.dart';
import '../../domain/entities/study_time.dart';

/// API'den gelen `/study-plans` yanıtını parse eden model.
/// Data katmanında kalır; domain katmanına StudyPlanEntity olarak iletilir.
class StudyPlanModel {
  const StudyPlanModel({
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
  final String? plannedStartTime;
  final String? plannedEndTime;
  final String status;
  final int completedQuestionCount;
  final int completedMinutes;
  final int orderIndex;
  final DateTime studyDate;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory StudyPlanModel.fromJson(Map<String, dynamic> json) {
    return StudyPlanModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      title: json['title'] as String,
      subject: json['subject'] as String,
      topic: json['topic'] as String?,
      targetQuestionCount: json['target_question_count'] as int,
      estimatedMinutes: json['estimated_minutes'] as int,
      plannedStartTime: json['planned_start_time'] as String?,
      plannedEndTime: json['planned_end_time'] as String?,
      status: json['status'] as String,
      completedQuestionCount: json['completed_question_count'] as int,
      completedMinutes: json['completed_minutes'] as int,
      orderIndex: json['order_index'] as int,
      studyDate: DateTime.parse(json['study_date'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  StudyPlanEntity toEntity() {
    return StudyPlanEntity(
      id: id,
      userId: userId,
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      plannedStartTime: StudyTime.fromApi(plannedStartTime),
      plannedEndTime: StudyTime.fromApi(plannedEndTime),
      status: StudyPlanStatus.fromApi(status),
      completedQuestionCount: completedQuestionCount,
      completedMinutes: completedMinutes,
      orderIndex: orderIndex,
      studyDate: studyDate,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
}
