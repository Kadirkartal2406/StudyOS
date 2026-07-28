import 'package:dio/dio.dart';

import '../entities/ai_chat_entities.dart';

abstract class AiChatRepository {
  Future<ChatResultEntity> sendMessage({
    required String message,
    String? conversationId,
    CancelToken? cancelToken,
  });

  Future<List<ConversationSummaryEntity>> listConversations();

  Future<ConversationDetailEntity> getConversation(String id);

  Future<void> deleteConversation(String id);
}
