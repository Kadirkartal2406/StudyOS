import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/ai_chat/data/datasources/ai_chat_remote_datasource.dart';
import 'package:studyos_mobile/features/ai_chat/data/models/ai_chat_models.dart';
import 'package:studyos_mobile/features/ai_chat/data/repositories/ai_chat_repository_impl.dart';

class _MockRemote extends Mock implements AiChatRemoteDatasource {}

class _FakeCancelToken extends Fake implements CancelToken {}

void main() {
  late _MockRemote remote;
  late AiChatRepositoryImpl repository;

  setUpAll(() {
    registerFallbackValue(_FakeCancelToken());
  });

  setUp(() {
    remote = _MockRemote();
    repository = AiChatRepositoryImpl(remote);
  });

  test('sendMessage maps to entity', () async {
    when(
      () => remote.sendMessage(
        message: any(named: 'message'),
        conversationId: any(named: 'conversationId'),
        cancelToken: any(named: 'cancelToken'),
      ),
    ).thenAnswer(
      (_) async => ChatResultModel.fromJson({
        'conversation': {
          'id': 'c1',
          'title': 'Test',
          'context_version': '1',
          'system_prompt_version': 'v1',
          'created_at': '2026-07-16T10:00:00Z',
          'updated_at': '2026-07-16T10:00:00Z',
          'message_count': 2,
        },
        'user_message': {
          'id': 'm1',
          'conversation_id': 'c1',
          'role': 'user',
          'content': 'Hi',
          'created_at': '2026-07-16T10:00:00Z',
        },
        'assistant_message': {
          'id': 'm2',
          'conversation_id': 'c1',
          'role': 'assistant',
          'content': 'Hello',
          'created_at': '2026-07-16T10:00:01Z',
        },
      }),
    );

    final result = await repository.sendMessage(message: 'Hi');
    expect(result.assistantMessage.content, 'Hello');
  });
}
