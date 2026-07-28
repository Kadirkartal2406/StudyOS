import '../../domain/entities/exam_entity.dart';
import '../../domain/repositories/exam_repository.dart';
import '../datasources/exam_remote_datasource.dart';

class ExamRepositoryImpl implements ExamRepository {
  ExamRepositoryImpl(this._remote);

  final ExamRemoteDatasource _remote;

  @override
  Future<List<ExamEntity>> listExams({String? examType}) async {
    final rows = await _remote.listExams(examType: examType);
    return rows.map((e) => e.toEntity()).toList();
  }

  @override
  Future<ExamEntity> getExam(String id) async {
    return (await _remote.getExam(id)).toEntity();
  }

  @override
  Future<ExamWriteResult> createExam(Map<String, dynamic> body) async {
    final result = await _remote.createExam(body);
    return ExamWriteResult(
      exam: result.exam.toEntity(),
      milestones: result.milestones,
    );
  }

  @override
  Future<ExamEntity> updateExam(String id, Map<String, dynamic> body) async {
    return (await _remote.updateExam(id, body)).toEntity();
  }

  @override
  Future<ExamEntity> replaceResults(
    String id,
    List<Map<String, dynamic>> results,
  ) async {
    return (await _remote.replaceResults(id, results)).toEntity();
  }

  @override
  Future<void> deleteExam(String id) => _remote.deleteExam(id);

  @override
  Future<ExamStatisticsEntity> getStatistics() => _remote.getStatistics();

  @override
  Future<ExamTrendsEntity> getTrends() => _remote.getTrends();
}
