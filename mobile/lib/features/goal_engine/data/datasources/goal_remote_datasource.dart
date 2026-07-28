import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/goal_models.dart';

class GoalRemoteDatasource {
  const GoalRemoteDatasource(this._dio);

  final Dio _dio;

  Future<List<GoalModel>> listAll() => _list(ApiEndpoints.goals);

  Future<List<GoalModel>> listActive() => _list(ApiEndpoints.goalsActive);

  Future<List<GoalModel>> listCompleted() =>
      _list(ApiEndpoints.goalsCompleted);

  Future<List<GoalModel>> listWeekly() => _list(ApiEndpoints.goalsWeekly);

  Future<List<GoalModel>> listMonthly() => _list(ApiEndpoints.goalsMonthly);

  Future<GoalProgressModel> getProgress() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.goalsProgress,
      );
      return GoalProgressModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<GoalModel> getById(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.goal(id),
      );
      return GoalModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<GoalModel> create(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.goals,
        data: body,
      );
      return GoalModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<GoalModel> update(String id, Map<String, dynamic> body) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.goal(id),
        data: body,
      );
      return GoalModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<void> delete(String id) async {
    try {
      await _dio.delete<void>(ApiEndpoints.goal(id));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<GoalExplainModel> explain(String id) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.goalExplain(id),
      );
      return GoalExplainModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<GoalModel>> _list(String path) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(path);
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => GoalModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  dynamic _extractData(Map<String, dynamic>? responseData) {
    if (responseData == null) {
      throw const NetworkException(message: 'Boş yanıt alındı');
    }
    final success = responseData['success'] as bool? ?? false;
    if (!success) {
      final error = responseData['error'] as Map<String, dynamic>?;
      final message = error?['message'] as String? ?? 'Bilinmeyen hata';
      throw UnknownException(message: message);
    }
    return responseData['data'];
  }
}
