import 'question_enums.dart';

class QuestionRecordEntity {
  const QuestionRecordEntity({
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
  final QuestionDifficulty? difficulty;
  final QuestionSource? source;
  final ExamType? examType;
  final String? note;
  final double netScore;
  final DateTime createdAt;
  final DateTime updatedAt;

  double get correctRate =>
      questionCount == 0 ? 0 : (correctCount / questionCount) * 100;
}

class QuestionStatisticsOverviewEntity {
  const QuestionStatisticsOverviewEntity({
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
}

class QuestionDailyBucketEntity {
  const QuestionDailyBucketEntity({
    required this.date,
    required this.questionCount,
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.netScore,
    required this.durationMinutes,
  });

  final String date;
  final int questionCount;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final double netScore;
  final int durationMinutes;
}

class QuestionDistributionItemEntity {
  const QuestionDistributionItemEntity({
    required this.name,
    required this.questionCount,
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.netScore,
    required this.durationMinutes,
    required this.correctRate,
  });

  final String name;
  final int questionCount;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final double netScore;
  final int durationMinutes;
  final double correctRate;
}

class QuestionListPage {
  const QuestionListPage({
    required this.items,
    required this.page,
    required this.pageSize,
    required this.totalItems,
    required this.totalPages,
  });

  final List<QuestionRecordEntity> items;
  final int page;
  final int pageSize;
  final int totalItems;
  final int totalPages;
}
