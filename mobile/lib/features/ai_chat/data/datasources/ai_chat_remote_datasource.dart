import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/ai_chat_models.dart';

class AiChatRemoteDatasource {
  const AiChatRemoteDatasource(this._dio);

  final Dio _dio;

  Future<ChatResultModel> sendMessage({
    required String message,
    String? conversationId,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.aiChat,
        data: {
          'message': message,
          if (conversationId != null) 'conversation_id': conversationId,
        },
        cancelToken: cancelToken,
      );
      return ChatResultModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<ConversationSummaryModel>> listConversations() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiConversations,
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map(
            (e) =>
                ConversationSummaryModel.fromJson(e as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<ConversationDetailModel> getConversation(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiConversation(id),
      );
      return ConversationDetailModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<void> deleteConversation(String id) async {
    try {
      await _dio.delete<Map<String, dynamic>>(ApiEndpoints.aiConversation(id));
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
