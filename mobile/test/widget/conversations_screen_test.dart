import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/features/ai_chat/domain/entities/ai_chat_entities.dart';
import 'package:studyos_mobile/features/ai_chat/domain/repositories/ai_chat_repository.dart';
import 'package:studyos_mobile/features/ai_chat/presentation/providers/ai_chat_provider.dart';
import 'package:studyos_mobile/features/ai_chat/presentation/screens/conversations_screen.dart';

class _FakeRepo implements AiChatRepository {
  @override
  Future<void> deleteConversation(String id) async {}

  @override
  Future<ConversationDetailEntity> getConversation(String id) async {
    return ConversationDetailEntity(
      id: id,
      title: 'Test',
      contextVersion: '1',
      systemPromptVersion: 'v1',
      createdAt: DateTime.parse('2026-07-16T10:00:00Z'),
      updatedAt: DateTime.parse('2026-07-16T10:00:00Z'),
      messages: const [],
    );
  }

  @override
  Future<List<ConversationSummaryEntity>> listConversations() async {
    return [
      ConversationSummaryEntity(
        id: 'c1',
        title: 'Bugün ne çalışmalıyım?',
        contextVersion: '1',
        systemPromptVersion: 'v1',
        createdAt: DateTime.parse('2026-07-16T10:00:00Z'),
        updatedAt: DateTime.parse('2026-07-16T10:00:00Z'),
        messageCount: 2,
      ),
    ];
  }

  @override
  Future<ChatResultEntity> sendMessage({
    required String message,
    String? conversationId,
    CancelToken? cancelToken,
  }) async {
    throw UnimplementedError();
  }
}

void main() {
  testWidgets('Conversations ekranı başlık ve liste gösterir', (tester) async {
    final router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(path: '/', builder: (_, __) => const ConversationsScreen()),
        GoRoute(
          path: '/ai-chat/new',
          builder: (_, __) => const Scaffold(body: Text('new-chat')),
        ),
        GoRoute(
          path: '/ai-coach',
          builder: (_, __) => const Scaffold(body: Text('insights')),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          aiChatRepositoryProvider.overrideWithValue(_FakeRepo()),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('AI Sohbet'), findsOneWidget);
    expect(find.text('Bugün ne çalışmalıyım?'), findsOneWidget);
    expect(find.text('Yeni sohbet'), findsOneWidget);
  });
}
