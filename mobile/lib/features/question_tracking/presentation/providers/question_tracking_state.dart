import '../../domain/entities/question_record_entity.dart';

sealed class QuestionListState {
  const QuestionListState();
}

class QuestionListInitial extends QuestionListState {
  const QuestionListInitial();
}

class QuestionListLoading extends QuestionListState {
  const QuestionListLoading();
}

class QuestionListLoaded extends QuestionListState {
  const QuestionListLoaded(this.page);
  final QuestionListPage page;
}

class QuestionListError extends QuestionListState {
  const QuestionListError(this.message);
  final String message;
}

sealed class QuestionStatsState {
  const QuestionStatsState();
}

class QuestionStatsInitial extends QuestionStatsState {
  const QuestionStatsInitial();
}

class QuestionStatsLoading extends QuestionStatsState {
  const QuestionStatsLoading();
}

class QuestionStatsLoaded extends QuestionStatsState {
  const QuestionStatsLoaded({
    required this.overview,
    required this.daily,
    required this.subjects,
    required this.topics,
    required this.exams,
  });

  final QuestionStatisticsOverviewEntity overview;
  final List<QuestionDailyBucketEntity> daily;
  final List<QuestionDistributionItemEntity> subjects;
  final List<QuestionDistributionItemEntity> topics;
  final List<QuestionDistributionItemEntity> exams;
}

class QuestionStatsError extends QuestionStatsState {
  const QuestionStatsError(this.message);
  final String message;
}
