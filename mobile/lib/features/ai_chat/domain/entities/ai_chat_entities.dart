// AI Chat domain entities — Sprint-2.2

enum ChatMessageRole { system, user, assistant }

class ChatMessageEntity {
  const ChatMessageEntity({
    required this.id,
    required this.conversationId,
    required this.role,
    required this.content,
    required this.createdAt,
    this.metadata = const {},
  });

  final String id;
  final String conversationId;
  final ChatMessageRole role;
  final String content;
  final DateTime createdAt;
  final Map<String, dynamic> metadata;
}

class ConversationSummaryEntity {
  const ConversationSummaryEntity({
    required this.id,
    required this.title,
    required this.contextVersion,
    required this.systemPromptVersion,
    required this.createdAt,
    required this.updatedAt,
    this.messageCount = 0,
  });

  final String id;
  final String title;
  final String contextVersion;
  final String systemPromptVersion;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int messageCount;
}

class ConversationDetailEntity {
  const ConversationDetailEntity({
    required this.id,
    required this.title,
    required this.contextVersion,
    required this.systemPromptVersion,
    required this.createdAt,
    required this.updatedAt,
    this.messages = const [],
    this.metadata = const {},
  });

  final String id;
  final String title;
  final String contextVersion;
  final String systemPromptVersion;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<ChatMessageEntity> messages;
  final Map<String, dynamic> metadata;
}

class ChatResultEntity {
  const ChatResultEntity({
    required this.conversation,
    required this.userMessage,
    required this.assistantMessage,
  });

  final ConversationSummaryEntity conversation;
  final ChatMessageEntity userMessage;
  final ChatMessageEntity assistantMessage;
}
