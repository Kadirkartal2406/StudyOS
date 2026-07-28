/// Deneme sınavı domain entity'leri — Sprint-2.6
class ExamResultEntity {
  const ExamResultEntity({
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
}

class ExamEntity {
  const ExamEntity({
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
  final List<ExamResultEntity> results;
}

class ExamWriteResult {
  const ExamWriteResult({required this.exam, this.milestones = const []});

  final ExamEntity exam;
  final List<String> milestones;
}

class ExamStatisticsEntity {
  const ExamStatisticsEntity({
    required this.totalExams,
    required this.averageNet,
    required this.highestNet,
    required this.lowestNet,
    this.lastExamTitle,
    this.lastExamNet = 0,
    this.weekExams = 0,
    this.monthExams = 0,
    this.bySubject = const {},
  });

  final int totalExams;
  final String? lastExamTitle;
  final double lastExamNet;
  final double highestNet;
  final double lowestNet;
  final double averageNet;
  final int weekExams;
  final int monthExams;
  final Map<String, double> bySubject;
}

class ExamTrendsEntity {
  const ExamTrendsEntity({
    this.netOverTime = const [],
    this.bySubject = const [],
    this.correctWrongBlank = const {},
  });

  final List<({String title, DateTime date, double net})> netOverTime;
  final List<({String subject, double averageNet, int examCount})> bySubject;
  final Map<String, int> correctWrongBlank;
}
