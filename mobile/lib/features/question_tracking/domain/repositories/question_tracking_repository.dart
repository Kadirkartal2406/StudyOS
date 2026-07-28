import '../entities/question_enums.dart';
import '../entities/question_record_entity.dart';

abstract class QuestionTrackingRepository {
  Future<QuestionListPage> list({
    int page = 1,
    int pageSize = 20,
    String? subject,
    String? topic,
    ExamType? examType,
    QuestionSource? source,
  });

  Future<QuestionRecordEntity> getById(String id);

  Future<QuestionRecordEntity> create(Map<String, dynamic> body);

  Future<QuestionRecordEntity> update(String id, Map<String, dynamic> body);

  Future<void> delete(String id);

  Future<QuestionStatisticsOverviewEntity> getStatistics();

  Future<List<QuestionDailyBucketEntity>> getDaily({int days = 14});

  Future<List<QuestionDistributionItemEntity>> getSubjects();

  Future<List<QuestionDistributionItemEntity>> getTopics();

  Future<List<QuestionDistributionItemEntity>> getExams();
}
