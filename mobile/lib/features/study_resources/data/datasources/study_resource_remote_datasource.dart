import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/constants/app_config.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/study_resource_model.dart';

class StudyResourceRemoteDatasource {
  const StudyResourceRemoteDatasource(this._dio);

  final Dio _dio;

  Future<List<StudyResourceModel>> listResources({
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
    String? status,
    String? resourceType,
  }) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.resources,
        queryParameters: {
          if (studyPlanId != null) 'study_plan_id': studyPlanId,
          if (subjectCode != null) 'subject_code': subjectCode,
          if (topicCode != null) 'topic_code': topicCode,
          if (status != null) 'status': status,
          if (resourceType != null) 'resource_type': resourceType,
        },
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => StudyResourceModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<StudyResourceModel>> listPlanResources(String planId) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studyPlanResources(planId),
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map((e) => StudyResourceModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudyResourceModel> getResource(String id) async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.resource(id));
      return StudyResourceModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudyResourceModel> createResource(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.resources,
        data: body,
      );
      return StudyResourceModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudyResourceModel> createPlanResource(
    String planId,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studyPlanResources(planId),
        data: body,
      );
      return StudyResourceModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudyResourceModel> updateResource(
    String id,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.resource(id),
        data: body,
      );
      return StudyResourceModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<void> deleteResource(String id) async {
    try {
      await _dio.delete<Map<String, dynamic>>(ApiEndpoints.resource(id));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudyResourceModel> openResource(String id) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.resourceOpen(id),
      );
      return StudyResourceModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ResourceStatisticsModel> getStatistics() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.resourcesStatistics,
      );
      return ResourceStatisticsModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<String> uploadResourceFile(
    List<int> fileBytes,
    String filename, {
    String? filePath,
  }) async {
    try {
      final MultipartFile part;
      if (filePath != null && filePath.isNotEmpty) {
        part = await MultipartFile.fromFile(filePath, filename: filename);
      } else if (fileBytes.isNotEmpty) {
        part = MultipartFile.fromBytes(fileBytes, filename: filename);
      } else {
        throw const NetworkException(message: 'Dosya içeriği boş');
      }
      final formData = FormData.fromMap({'file': part});
      final response = await _dio.post<Map<String, dynamic>>(
        '/resources/upload',
        data: formData,
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      return _absoluteUrl(data['url'] as String);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// Backend `/uploads/...` gibi göreli yol döner; dosyanın açılabilmesi için
  /// API host'u ile birleştirilir (`/api/v1` yolu atılır).
  String _absoluteUrl(String url) {
    if (!url.startsWith('/')) return url;
    final base = Uri.parse(AppConfig.apiBaseUrl);
    return Uri(
      scheme: base.scheme,
      host: base.host,
      port: base.hasPort ? base.port : null,
      path: url,
    ).toString();
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
