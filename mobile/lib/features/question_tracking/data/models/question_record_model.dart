import '../../domain/entities/question_enums.dart';
import '../../domain/entities/question_record_entity.dart';

class QuestionRecordModel {
  const QuestionRecordModel({
    required this.id,
    required this.userId,
    required this.subject,
    required this.questionCount,
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.durationMinutes,
    required this.netScore,
    required this.createdAt,
    required this.updatedAt,
    this.topic,
    this.difficulty,
    this.source,
    this.examType,
    this.note,
    this.studyPlanId,
    this.studySessionId,
  });

  final String id;
  final String userId;
  final String? studyPlanId;
  final String? studySessionId;
  final String subject;
  final String? topic;
  final int questionCount;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final int durationMinutes;
  final String? difficulty;
  final String? source;
  final String? examType;
  final String? note;
  final double netScore;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory QuestionRecordModel.fromJson(Map<String, dynamic> json) {
    return QuestionRecordModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      studyPlanId: json['study_plan_id'] as String?,
      studySessionId: json['study_session_id'] as String?,
      subject: json['subject'] as String,
      topic: json['topic'] as String?,
      questionCount: json['question_count'] as int,
      correctCount: json['correct_count'] as int? ?? 0,
      wrongCount: json['wrong_count'] as int? ?? 0,
      blankCount: json['blank_count'] as int? ?? 0,
      durationMinutes: json['duration_minutes'] as int? ?? 0,
      difficulty: json['difficulty'] as String?,
      source: json['source'] as String?,
      examType: json['exam_type'] as String?,
      note: json['note'] as String?,
      netScore: parseNetScore(json['net_score']),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  QuestionRecordEntity toEntity() => QuestionRecordEntity(
        id: id,
        userId: userId,
        studyPlanId: studyPlanId,
        studySessionId: studySessionId,
        subject: subject,
        topic: topic,
        questionCount: questionCount,
        correctCount: correctCount,
        wrongCount: wrongCount,
        blankCount: blankCount,
        durationMinutes: durationMinutes,
        difficulty: QuestionDifficulty.fromApi(difficulty),
        source: QuestionSource.fromApi(source),
        examType: ExamType.fromApi(examType),
        note: note,
        netScore: netScore,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );
}

double parseNetScore(Object? value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0;
  return 0;
}


class QuestionStatisticsOverviewModel {
  factory QuestionStatisticsOverviewModel.fromJson(Map<String, dynamic> json) {
    return QuestionStatisticsOverviewModel._(
      totalQuestions: json['total_questions'] as int? ?? 0,
      todayQuestions: json['today_questions'] as int? ?? 0,
      weekQuestions: json['week_questions'] as int? ?? 0,
      monthQuestions: json['month_questions'] as int? ?? 0,
      totalCorrect: json['total_correct'] as int? ?? 0,
      totalWrong: json['total_wrong'] as int? ?? 0,
      totalBlank: json['total_blank'] as int? ?? 0,
      correctRate: (json['correct_rate'] as num?)?.toDouble() ?? 0,
      wrongRate: (json['wrong_rate'] as num?)?.toDouble() ?? 0,
      totalNet: parseNetScore(json['total_net']),
      totalDurationMinutes: json['total_duration_minutes'] as int? ?? 0,
      recordCount: json['record_count'] as int? ?? 0,
    );
  }

  const QuestionStatisticsOverviewModel._({
    required this.totalQuestions,
    required this.todayQuestions,
    required this.weekQuestions,
    required this.monthQuestions,
    required this.totalCorrect,
    required this.totalWrong,
    required this.totalBlank,
    required this.correctRate,
    required this.wrongRate,
    required this.totalNet,
    required this.totalDurationMinutes,
    required this.recordCount,
  });

  final int totalQuestions;
  final int todayQuestions;
  final int weekQuestions;
  final int monthQuestions;
  final int totalCorrect;
  final int totalWrong;
  final int totalBlank;
  final double correctRate;
  final double wrongRate;
  final double totalNet;
  final int totalDurationMinutes;
  final int recordCount;

  QuestionStatisticsOverviewEntity toEntity() =>
      QuestionStatisticsOverviewEntity(
        totalQuestions: totalQuestions,
        todayQuestions: todayQuestions,
        weekQuestions: weekQuestions,
        monthQuestions: monthQuestions,
        totalCorrect: totalCorrect,
        totalWrong: totalWrong,
        totalBlank: totalBlank,
        correctRate: correctRate,
        wrongRate: wrongRate,
        totalNet: totalNet,
        totalDurationMinutes: totalDurationMinutes,
        recordCount: recordCount,
      );
}
