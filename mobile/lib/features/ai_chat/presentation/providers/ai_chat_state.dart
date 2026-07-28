import '../../domain/entities/ai_chat_entities.dart';

sealed class AiChatState {
  const AiChatState();
}

final class AiChatInitial extends AiChatState {
  const AiChatInitial();
}

final class AiChatLoading extends AiChatState {
  const AiChatLoading();
}

final class AiChatLoaded extends AiChatState {
  const AiChatLoaded({
    required this.conversations,
    this.activeConversationId,
    this.messages = const [],
    this.isTyping = false,
    this.sending = false,
    this.errorMessage,
  });

  final List<ConversationSummaryEntity> conversations;
  final String? activeConversationId;
  final List<ChatMessageEntity> messages;
  final bool isTyping;
  final bool sending;
  final String? errorMessage;

  AiChatLoaded copyWith({
    List<ConversationSummaryEntity>? conversations,
    String? activeConversationId,
    List<ChatMessageEntity>? messages,
    bool? isTyping,
    bool? sending,
    String? errorMessage,
    bool clearError = false,
  }) {
    return AiChatLoaded(
      conversations: conversations ?? this.conversations,
      activeConversationId: activeConversationId ?? this.activeConversationId,
      messages: messages ?? this.messages,
      isTyping: isTyping ?? this.isTyping,
      sending: sending ?? this.sending,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

final class AiChatError extends AiChatState {
  const AiChatError(this.message);

  final String message;
}
