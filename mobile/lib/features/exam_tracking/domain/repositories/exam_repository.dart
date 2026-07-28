import '../entities/exam_entity.dart';

abstract class ExamRepository {
  Future<List<ExamEntity>> listExams({String? examType});
  Future<ExamEntity> getExam(String id);
  Future<ExamWriteResult> createExam(Map<String, dynamic> body);
  Future<ExamEntity> updateExam(String id, Map<String, dynamic> body);
  Future<ExamEntity> replaceResults(String id, List<Map<String, dynamic>> results);
  Future<void> deleteExam(String id);
  Future<ExamStatisticsEntity> getStatistics();
  Future<ExamTrendsEntity> getTrends();
}
