import '../../domain/entities/ai_chat_entities.dart';

Map<String, dynamic> _asStringKeyMap(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) {
    return value.map((key, val) => MapEntry(key.toString(), val));
  }
  return {};
}

ChatMessageRole _roleFrom(String value) {
  return switch (value) {
    'system' => ChatMessageRole.system,
    'assistant' => ChatMessageRole.assistant,
    _ => ChatMessageRole.user,
  };
}

class ChatMessageModel {
  const ChatMessageModel({
    required this.id,
    required this.conversationId,
    required this.role,
    required this.content,
    required this.createdAt,
    this.metadata = const {},
  });

  final String id;
  final String conversationId;
  final String role;
  final String content;
  final DateTime createdAt;
  final Map<String, dynamic> metadata;

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) {
    return ChatMessageModel(
      id: json['id'] as String,
      conversationId: json['conversation_id'] as String,
      role: json['role'] as String,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      metadata: _asStringKeyMap(json['metadata']),
    );
  }

  ChatMessageEntity toEntity() => ChatMessageEntity(
        id: id,
        conversationId: conversationId,
        role: _roleFrom(role),
        content: content,
        createdAt: createdAt,
        metadata: metadata,
      );
}

class ConversationSummaryModel {
  const ConversationSummaryModel({
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

  factory ConversationSummaryModel.fromJson(Map<String, dynamic> json) {
    return ConversationSummaryModel(
      id: json['id'] as String,
      title: json['title'] as String,
      contextVersion: json['context_version'] as String? ?? '1',
      systemPromptVersion: json['system_prompt_version'] as String? ?? 'v1',
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      messageCount: json['message_count'] as int? ?? 0,
    );
  }

  ConversationSummaryEntity toEntity() => ConversationSummaryEntity(
        id: id,
        title: title,
        contextVersion: contextVersion,
        systemPromptVersion: systemPromptVersion,
        createdAt: createdAt,
        updatedAt: updatedAt,
        messageCount: messageCount,
      );
}

class ConversationDetailModel {
  const ConversationDetailModel({
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
  final List<ChatMessageModel> messages;
  final Map<String, dynamic> metadata;

  factory ConversationDetailModel.fromJson(Map<String, dynamic> json) {
    final msgs = json['messages'] as List<dynamic>? ?? [];
    return ConversationDetailModel(
      id: json['id'] as String,
      title: json['title'] as String,
      contextVersion: json['context_version'] as String? ?? '1',
      systemPromptVersion: json['system_prompt_version'] as String? ?? 'v1',
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      messages: msgs
          .map((e) => ChatMessageModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      metadata: _asStringKeyMap(json['metadata']),
    );
  }

  ConversationDetailEntity toEntity() => ConversationDetailEntity(
        id: id,
        title: title,
        contextVersion: contextVersion,
        systemPromptVersion: systemPromptVersion,
        createdAt: createdAt,
        updatedAt: updatedAt,
        messages: messages.map((e) => e.toEntity()).toList(),
        metadata: metadata,
      );
}

class ChatResultModel {
  const ChatResultModel({
    required this.conversation,
    required this.userMessage,
    required this.assistantMessage,
  });

  final ConversationSummaryModel conversation;
  final ChatMessageModel userMessage;
  final ChatMessageModel assistantMessage;

  factory ChatResultModel.fromJson(Map<String, dynamic> json) {
    var assistant = ChatMessageModel.fromJson(
      json['assistant_message'] as Map<String, dynamic>,
    );
    final topLevel = json['plan_proposal'];
    if (topLevel is Map &&
        !assistant.metadata.containsKey('plan_proposal')) {
      final meta = Map<String, dynamic>.from(assistant.metadata);
      meta['plan_proposal'] = _asStringKeyMap(topLevel);
      assistant = ChatMessageModel(
        id: assistant.id,
        conversationId: assistant.conversationId,
        role: assistant.role,
        content: assistant.content,
        createdAt: assistant.createdAt,
        metadata: meta,
      );
    }
    return ChatResultModel(
      conversation: ConversationSummaryModel.fromJson(
        json['conversation'] as Map<String, dynamic>,
      ),
      userMessage: ChatMessageModel.fromJson(
        json['user_message'] as Map<String, dynamic>,
      ),
      assistantMessage: assistant,
    );
  }

  ChatResultEntity toEntity() => ChatResultEntity(
        conversation: conversation.toEntity(),
        userMessage: userMessage.toEntity(),
        assistantMessage: assistantMessage.toEntity(),
      );
}
