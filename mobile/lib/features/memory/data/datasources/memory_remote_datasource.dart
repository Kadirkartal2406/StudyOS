import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/memory_model.dart';

class MemoryRemoteDatasource {
  const MemoryRemoteDatasource(this._dio);

  final Dio _dio;

  Future<List<MemoryModel>> listMemories({bool activeOnly = true}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.memory,
        queryParameters: {'active_only': activeOnly},
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => MemoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<MemoryModel> getMemory(String id) async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.memoryItem(id));
      return MemoryModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<MemoryModel> createMemory(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.memory,
        data: body,
      );
      return MemoryModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<MemoryModel> updateMemory(String id, Map<String, dynamic> body) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.memoryItem(id),
        data: body,
      );
      return MemoryModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<void> deleteMemory(String id) async {
    try {
      await _dio.delete<Map<String, dynamic>>(ApiEndpoints.memoryItem(id));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<MemoryModel>> search(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.memorySearch,
        data: body,
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => MemoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<MemorySettingsModel> getSettings() async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.memorySettings);
      return MemorySettingsModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<MemorySettingsModel> updateSettings({required bool enabled}) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.memorySettings,
        data: {'ai_memory_enabled': enabled},
      );
      return MemorySettingsModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<MemoryModel>> exportMemories() async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.memoryExport);
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => MemoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<int> clearMemories() async {
    try {
      final response =
          await _dio.delete<Map<String, dynamic>>(ApiEndpoints.memoryClear);
      final data = _extractData(response.data) as Map<String, dynamic>;
      return data['deleted'] as int? ?? 0;
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
