import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/dashboard_model.dart';

/// Backend `/dashboard` endpoint'ine doğrudan erişen datasource.
/// Yalnızca ham API çağrıları içerir — iş mantığı yok.
class DashboardRemoteDatasource {
  const DashboardRemoteDatasource(this._dio);

  final Dio _dio;

  /// GET /dashboard
  Future<DashboardModel> getDashboard() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.dashboard,
      );
      final data = _extractData(response.data);
      return DashboardModel.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// API yanıtındaki `data` alanını çıkarır; hata durumunda exception fırlatır.
  Map<String, dynamic> _extractData(Map<String, dynamic>? responseData) {
    if (responseData == null) {
      throw const NetworkException(message: 'Boş yanıt alındı');
    }
    final success = responseData['success'] as bool? ?? false;
    if (!success) {
      final error = responseData['error'] as Map<String, dynamic>?;
      final message = error?['message'] as String? ?? 'Bilinmeyen hata';
      throw UnknownException(message: message);
    }
    return responseData['data'] as Map<String, dynamic>;
  }
}
