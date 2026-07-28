import 'package:dio/dio.dart';
import 'package:intl/intl.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/statistics_models.dart';

class StatisticsRemoteDatasource {
  const StatisticsRemoteDatasource(this._dio);

  final Dio _dio;
  static final DateFormat _dateFormat = DateFormat('yyyy-MM-dd');

  Future<StatisticsOverviewModel> getOverview() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsOverview,
      );
      return StatisticsOverviewModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StatisticsDailyModel> getDaily({DateTime? date}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsDaily,
        queryParameters: date == null
            ? null
            : {'date': _dateFormat.format(date)},
      );
      return StatisticsDailyModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StatisticsPeriodModel> getWeekly({DateTime? anchor}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsWeekly,
        queryParameters: anchor == null
            ? null
            : {'anchor': _dateFormat.format(anchor)},
      );
      return StatisticsPeriodModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StatisticsPeriodModel> getMonthly({DateTime? anchor}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsMonthly,
        queryParameters: anchor == null
            ? null
            : {'anchor': _dateFormat.format(anchor)},
      );
      return StatisticsPeriodModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StatisticsDistributionModel> getSubjects() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsSubjects,
      );
      return StatisticsDistributionModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StatisticsDistributionModel> getTopics() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsTopics,
      );
      return StatisticsDistributionModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StatisticsHeatmapModel> getHeatmap() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.statisticsHeatmap,
      );
      return StatisticsHeatmapModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
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
