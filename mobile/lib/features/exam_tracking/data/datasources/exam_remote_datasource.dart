import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/exam_entity.dart';
import '../models/exam_model.dart';

class ExamRemoteDatasource {
  const ExamRemoteDatasource(this._dio);

  final Dio _dio;

  Future<List<ExamModel>> listExams({String? examType}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.exams,
        queryParameters: {if (examType != null) 'exam_type': examType},
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => ExamModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ExamModel> getExam(String id) async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.exam(id));
      return ExamModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<({ExamModel exam, List<String> milestones})> createExam(
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.exams,
        data: body,
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final exam = ExamModel.fromJson(data['exam'] as Map<String, dynamic>);
      final milestones = (data['milestones'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList();
      return (exam: exam, milestones: milestones);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ExamModel> updateExam(String id, Map<String, dynamic> body) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.exam(id),
        data: body,
      );
      return ExamModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ExamModel> replaceResults(
    String id,
    List<Map<String, dynamic>> results,
  ) async {
    try {
      final response = await _dio.put<Map<String, dynamic>>(
        ApiEndpoints.examResults(id),
        data: {'results': results},
      );
      return ExamModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<void> deleteExam(String id) async {
    try {
      await _dio.delete<Map<String, dynamic>>(ApiEndpoints.exam(id));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ExamStatisticsEntity> getStatistics() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examsStatistics,
      );
      final json = _extractData(response.data) as Map<String, dynamic>;
      final bySubjectRaw = json['by_subject'] as Map<String, dynamic>? ?? {};
      return ExamStatisticsEntity(
        totalExams: json['total_exams'] as int? ?? 0,
        lastExamTitle: json['last_exam_title'] as String?,
        lastExamNet: (json['last_exam_net'] as num?)?.toDouble() ?? 0,
        highestNet: (json['highest_net'] as num?)?.toDouble() ?? 0,
        lowestNet: (json['lowest_net'] as num?)?.toDouble() ?? 0,
        averageNet: (json['average_net'] as num?)?.toDouble() ?? 0,
        weekExams: json['week_exams'] as int? ?? 0,
        monthExams: json['month_exams'] as int? ?? 0,
        bySubject: bySubjectRaw.map(
          (k, v) => MapEntry(k, (v as num).toDouble()),
        ),
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ExamTrendsEntity> getTrends() async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.examsTrends);
      final json = _extractData(response.data) as Map<String, dynamic>;
      final netList = json['net_over_time'] as List<dynamic>? ?? [];
      final subjectList = json['by_subject'] as List<dynamic>? ?? [];
      final cwb = json['correct_wrong_blank'] as Map<String, dynamic>? ?? {};
      return ExamTrendsEntity(
        netOverTime: netList.map((e) {
          final m = e as Map<String, dynamic>;
          return (
            title: m['title'] as String? ?? '',
            date: DateTime.parse(m['exam_date'] as String),
            net: (m['total_net'] as num?)?.toDouble() ?? 0,
          );
        }).toList(),
        bySubject: subjectList.map((e) {
          final m = e as Map<String, dynamic>;
          return (
            subject: m['subject'] as String? ?? '',
            averageNet: (m['average_net'] as num?)?.toDouble() ?? 0,
            examCount: m['exam_count'] as int? ?? 0,
          );
        }).toList(),
        correctWrongBlank: cwb.map((k, v) => MapEntry(k, (v as num).toInt())),
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  dynamic _extractData(Map<String, dynamic>? body) {
    if (body == null) return null;
    return body['data'];
  }
}
