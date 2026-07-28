import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/ai_chat_remote_datasource.dart';
import '../../data/repositories/ai_chat_repository_impl.dart';
import '../../domain/entities/ai_chat_entities.dart';
import '../../domain/repositories/ai_chat_repository.dart';
import 'ai_chat_state.dart';

final _remoteProvider = Provider<AiChatRemoteDatasource>((ref) {
  return AiChatRemoteDatasource(ref.watch(dioClientProvider));
});

final aiChatRepositoryProvider = Provider<AiChatRepository>((ref) {
  return AiChatRepositoryImpl(ref.watch(_remoteProvider));
});

class AiChatNotifier extends StateNotifier<AiChatState> {
  AiChatNotifier(this._repository) : super(const AiChatInitial()) {
    loadConversations();
  }

  final AiChatRepository _repository;
  CancelToken? _sendToken;

  /// Stream-ready hook — gerçek SSE sonraki sprint.
  Future<void> onStreamChunk(String chunk) async {}

  Future<void> loadConversations() async {
    state = const AiChatLoading();
    try {
      final items = await _repository.listConversations();
      state = AiChatLoaded(conversations: items);
    } on AppException catch (e) {
      state = AiChatError(e.message);
    } catch (_) {
      state = const AiChatError('Sohbetler yüklenemedi');
    }
  }

  Future<void> openConversation(String id) async {
    final current = state;
    if (current is! AiChatLoaded) return;
    state = current.copyWith(isTyping: true, clearError: true);
    try {
      final detail = await _repository.getConversation(id);
      state = current.copyWith(
        activeConversationId: detail.id,
        messages: detail.messages
            .where((m) => m.role != ChatMessageRole.system)
            .toList(),
        isTyping: false,
      );
    } on AppException catch (e) {
      state = current.copyWith(isTyping: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isTyping: false,
        errorMessage: 'Sohbet açılamadı',
      );
    }
  }

  void startNewChat() {
    final current = state;
    final List<ConversationSummaryEntity> convs =
        current is AiChatLoaded ? current.conversations : const [];
    state = AiChatLoaded(
      conversations: convs,
      activeConversationId: null,
      messages: const [],
    );
  }

  Future<void> sendMessage(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return;

    var current = state;
    if (current is! AiChatLoaded) {
      current = const AiChatLoaded(conversations: []);
      state = current;
    }

    _sendToken?.cancel();
    _sendToken = CancelToken();
    state = current.copyWith(sending: true, isTyping: true, clearError: true);
    try {
      final result = await _repository.sendMessage(
        message: trimmed,
        conversationId: current.activeConversationId,
        cancelToken: _sendToken,
      );
      final updatedMessages = [
        ...current.messages,
        result.userMessage,
        result.assistantMessage,
      ];
      final convs = await _repository.listConversations();
      state = AiChatLoaded(
        conversations: convs,
        activeConversationId: result.conversation.id,
        messages: updatedMessages,
        sending: false,
        isTyping: false,
      );
    } on CancelledException {
      state = current.copyWith(
        sending: false,
        isTyping: false,
        errorMessage: 'İstek iptal edildi',
      );
    } on AiProviderException catch (e) {
      state = current.copyWith(
        sending: false,
        isTyping: false,
        errorMessage: _friendlyAiError(e),
      );
    } on AppException catch (e) {
      state = current.copyWith(
        sending: false,
        isTyping: false,
        errorMessage: e.message,
      );
    } catch (_) {
      state = current.copyWith(
        sending: false,
        isTyping: false,
        errorMessage: 'Mesaj gönderilemedi',
      );
    } finally {
      _sendToken = null;
    }
  }

  String _friendlyAiError(AiProviderException e) {
    return switch (e.code) {
      'AI_QUOTA_EXCEEDED' => 'AI kotası doldu. Daha sonra tekrar deneyin.',
      'AI_RATE_LIMIT' => 'AI hız limiti aşıldı. Biraz bekleyip tekrar deneyin.',
      'AI_TIMEOUT' => 'AI yanıtı zaman aşımına uğradı.',
      'AI_UNAVAILABLE' => 'AI sağlayıcı kullanılamıyor.',
      _ => e.message,
    };
  }

  void cancelSend() {
    _sendToken?.cancel('user_cancel');
    _sendToken = null;
    final current = state;
    if (current is AiChatLoaded && current.sending) {
      state = current.copyWith(
        sending: false,
        isTyping: false,
        errorMessage: 'İstek iptal edildi',
      );
    }
  }

  /// Son kullanıcı mesajını yeniden gönder (ağ/hata sonrası).
  Future<void> retryLast() async {
    final current = state;
    if (current is! AiChatLoaded || current.messages.isEmpty) return;
    final lastUser = current.messages.lastWhere(
      (m) => m.role == ChatMessageRole.user,
      orElse: () => current.messages.last,
    );
    if (lastUser.role != ChatMessageRole.user) return;
    await sendMessage(lastUser.content);
  }

  /// Son asistan yanıtını UI'dan düşürüp son kullanıcı mesajını yeniden gönder.
  Future<void> regenerate() async {
    final current = state;
    if (current is! AiChatLoaded || current.messages.isEmpty) return;
    var messages = List<ChatMessageEntity>.from(current.messages);
    if (messages.isNotEmpty &&
        messages.last.role == ChatMessageRole.assistant) {
      messages = messages.sublist(0, messages.length - 1);
      state = current.copyWith(messages: messages, clearError: true);
    }
    final lastUser = messages.lastWhere(
      (m) => m.role == ChatMessageRole.user,
      orElse: () => messages.last,
    );
    if (lastUser.role != ChatMessageRole.user) return;
    await sendMessage(lastUser.content);
  }

  Future<void> deleteConversation(String id) async {
    final current = state;
    if (current is! AiChatLoaded) return;
    try {
      await _repository.deleteConversation(id);
      final convs = await _repository.listConversations();
      final clearing = current.activeConversationId == id;
      state = current.copyWith(
        conversations: convs,
        activeConversationId: clearing ? null : current.activeConversationId,
        messages: clearing ? const [] : current.messages,
      );
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }
}

final aiChatProvider =
    StateNotifierProvider<AiChatNotifier, AiChatState>((ref) {
  return AiChatNotifier(ref.watch(aiChatRepositoryProvider));
});
