import '../../domain/entities/exam_entity.dart';

class ExamResultModel {
  const ExamResultModel({
    required this.id,
    required this.examId,
    required this.subject,
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.questionCount,
    required this.netScore,
    required this.durationMinutes,
  });

  final String id;
  final String examId;
  final String subject;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final int questionCount;
  final double netScore;
  final int durationMinutes;

  factory ExamResultModel.fromJson(Map<String, dynamic> json) {
    return ExamResultModel(
      id: json['id'] as String,
      examId: json['exam_id'] as String,
      subject: json['subject'] as String,
      correctCount: json['correct_count'] as int? ?? 0,
      wrongCount: json['wrong_count'] as int? ?? 0,
      blankCount: json['blank_count'] as int? ?? 0,
      questionCount: json['question_count'] as int? ?? 0,
      netScore: _asDouble(json['net_score']),
      durationMinutes: json['duration_minutes'] as int? ?? 0,
    );
  }

  ExamResultEntity toEntity() => ExamResultEntity(
        id: id,
        examId: examId,
        subject: subject,
        correctCount: correctCount,
        wrongCount: wrongCount,
        blankCount: blankCount,
        questionCount: questionCount,
        netScore: netScore,
        durationMinutes: durationMinutes,
      );
}

class ExamModel {
  const ExamModel({
    required this.id,
    required this.userId,
    required this.title,
    required this.examType,
    required this.examDate,
    required this.durationMinutes,
    required this.totalNet,
    required this.totalQuestions,
    required this.resultCount,
    this.notes,
    this.results = const [],
  });

  final String id;
  final String userId;
  final String title;
  final String examType;
  final DateTime examDate;
  final int durationMinutes;
  final String? notes;
  final double totalNet;
  final int totalQuestions;
  final int resultCount;
  final List<ExamResultModel> results;

  factory ExamModel.fromJson(Map<String, dynamic> json) {
    final resultsJson = json['results'] as List<dynamic>? ?? [];
    return ExamModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      title: json['title'] as String,
      examType: json['exam_type'] as String? ?? 'custom',
      examDate: DateTime.parse(json['exam_date'] as String),
      durationMinutes: json['duration_minutes'] as int? ?? 0,
      notes: json['notes'] as String?,
      totalNet: _asDouble(json['total_net']),
      totalQuestions: json['total_questions'] as int? ?? 0,
      resultCount: json['result_count'] as int? ?? 0,
      results: resultsJson
          .map((e) => ExamResultModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  ExamEntity toEntity() => ExamEntity(
        id: id,
        userId: userId,
        title: title,
        examType: examType,
        examDate: examDate,
        durationMinutes: durationMinutes,
        notes: notes,
        totalNet: totalNet,
        totalQuestions: totalQuestions,
        resultCount: resultCount,
        results: results.map((e) => e.toEntity()).toList(),
      );
}

double _asDouble(dynamic value) {
  if (value == null) return 0;
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0;
  return 0;
}
