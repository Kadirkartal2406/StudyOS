import '../../domain/entities/exam_entity.dart';

sealed class ExamState {
  const ExamState();
}

class ExamInitial extends ExamState {
  const ExamInitial();
}

class ExamLoading extends ExamState {
  const ExamLoading();
}

class ExamLoaded extends ExamState {
  const ExamLoaded({
    required this.items,
    this.statistics,
    this.trends,
    this.errorMessage,
  });

  final List<ExamEntity> items;
  final ExamStatisticsEntity? statistics;
  final ExamTrendsEntity? trends;
  final String? errorMessage;
}

class ExamError extends ExamState {
  const ExamError(this.message);

  final String message;
}
