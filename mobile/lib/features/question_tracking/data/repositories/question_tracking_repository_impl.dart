import '../../../../core/constants/api_endpoints.dart';
import '../../domain/entities/question_enums.dart';
import '../../domain/entities/question_record_entity.dart';
import '../../domain/repositories/question_tracking_repository.dart';
import '../datasources/question_tracking_remote_datasource.dart';

class QuestionTrackingRepositoryImpl implements QuestionTrackingRepository {
  const QuestionTrackingRepositoryImpl(this._remote);

  final QuestionTrackingRemoteDatasource _remote;

  @override
  Future<QuestionListPage> list({
    int page = 1,
    int pageSize = 20,
    String? subject,
    String? topic,
    ExamType? examType,
    QuestionSource? source,
  }) async {
    final (models, pagination) = await _remote.list(
      page: page,
      pageSize: pageSize,
      subject: subject,
      topic: topic,
      examType: examType?.apiValue,
      source: source?.apiValue,
    );
    return QuestionListPage(
      items: models.map((m) => m.toEntity()).toList(),
      page: pagination['page'] as int? ?? page,
      pageSize: pagination['page_size'] as int? ?? pageSize,
      totalItems: pagination['total_items'] as int? ?? models.length,
      totalPages: pagination['total_pages'] as int? ?? 1,
    );
  }

  @override
  Future<QuestionRecordEntity> getById(String id) async {
    final model = await _remote.getById(id);
    return model.toEntity();
  }

  @override
  Future<QuestionRecordEntity> create(Map<String, dynamic> body) async {
    final model = await _remote.create(body);
    return model.toEntity();
  }

  @override
  Future<QuestionRecordEntity> update(
    String id,
    Map<String, dynamic> body,
  ) async {
    final model = await _remote.update(id, body);
    return model.toEntity();
  }

  @override
  Future<void> delete(String id) => _remote.delete(id);

  @override
  Future<QuestionStatisticsOverviewEntity> getStatistics() async {
    final model = await _remote.getStatistics();
    return model.toEntity();
  }

  @override
  Future<List<QuestionDailyBucketEntity>> getDaily({int days = 14}) =>
      _remote.getDaily(days: days);

  @override
  Future<List<QuestionDistributionItemEntity>> getSubjects() =>
      _remote.getDistribution(ApiEndpoints.questionsSubjects);

  @override
  Future<List<QuestionDistributionItemEntity>> getTopics() =>
      _remote.getDistribution(ApiEndpoints.questionsTopics);

  @override
  Future<List<QuestionDistributionItemEntity>> getExams() =>
      _remote.getDistribution(ApiEndpoints.questionsExams);
}
