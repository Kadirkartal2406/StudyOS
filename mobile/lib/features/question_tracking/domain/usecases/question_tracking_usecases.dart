import '../entities/question_enums.dart';
import '../entities/question_record_entity.dart';
import '../repositories/question_tracking_repository.dart';

class GetQuestionsUsecase {
  const GetQuestionsUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<QuestionListPage> call({
    int page = 1,
    String? subject,
    ExamType? examType,
  }) =>
      _repo.list(page: page, subject: subject, examType: examType);
}

class GetQuestionByIdUsecase {
  const GetQuestionByIdUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<QuestionRecordEntity> call(String id) => _repo.getById(id);
}

class CreateQuestionUsecase {
  const CreateQuestionUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<QuestionRecordEntity> call(Map<String, dynamic> body) =>
      _repo.create(body);
}

class UpdateQuestionUsecase {
  const UpdateQuestionUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<QuestionRecordEntity> call(String id, Map<String, dynamic> body) =>
      _repo.update(id, body);
}

class DeleteQuestionUsecase {
  const DeleteQuestionUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<void> call(String id) => _repo.delete(id);
}

class GetQuestionStatisticsUsecase {
  const GetQuestionStatisticsUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<QuestionStatisticsOverviewEntity> call() => _repo.getStatistics();
}

class GetQuestionDailyUsecase {
  const GetQuestionDailyUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<List<QuestionDailyBucketEntity>> call({int days = 14}) =>
      _repo.getDaily(days: days);
}

class GetQuestionSubjectsUsecase {
  const GetQuestionSubjectsUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<List<QuestionDistributionItemEntity>> call() => _repo.getSubjects();
}

class GetQuestionTopicsUsecase {
  const GetQuestionTopicsUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<List<QuestionDistributionItemEntity>> call() => _repo.getTopics();
}

class GetQuestionExamsUsecase {
  const GetQuestionExamsUsecase(this._repo);
  final QuestionTrackingRepository _repo;

  Future<List<QuestionDistributionItemEntity>> call() => _repo.getExams();
}
