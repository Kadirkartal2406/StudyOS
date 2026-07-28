import 'package:dio/dio.dart';

import '../../domain/entities/ai_chat_entities.dart';
import '../../domain/repositories/ai_chat_repository.dart';
import '../datasources/ai_chat_remote_datasource.dart';

class AiChatRepositoryImpl implements AiChatRepository {
  const AiChatRepositoryImpl(this._remote);

  final AiChatRemoteDatasource _remote;

  @override
  Future<ChatResultEntity> sendMessage({
    required String message,
    String? conversationId,
    CancelToken? cancelToken,
  }) async {
    final model = await _remote.sendMessage(
      message: message,
      conversationId: conversationId,
      cancelToken: cancelToken,
    );
    return model.toEntity();
  }

  @override
  Future<List<ConversationSummaryEntity>> listConversations() async {
    final models = await _remote.listConversations();
    return models.map((e) => e.toEntity()).toList();
  }

  @override
  Future<ConversationDetailEntity> getConversation(String id) async {
    final model = await _remote.getConversation(id);
    return model.toEntity();
  }

  @override
  Future<void> deleteConversation(String id) async {
    await _remote.deleteConversation(id);
  }
}
