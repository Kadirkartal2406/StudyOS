import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/ai_chat/data/models/ai_chat_models.dart';

void main() {
  test('ChatResultModel.fromJson maps conversation and messages', () {
    final model = ChatResultModel.fromJson({
      'conversation': {
        'id': 'c1',
        'title': 'Merhaba',
        'context_version': '1',
        'system_prompt_version': 'v1',
        'created_at': '2026-07-16T10:00:00Z',
        'updated_at': '2026-07-16T10:01:00Z',
        'message_count': 2,
      },
      'user_message': {
        'id': 'm1',
        'conversation_id': 'c1',
        'role': 'user',
        'content': 'Selam',
        'created_at': '2026-07-16T10:00:00Z',
        'metadata': {},
      },
      'assistant_message': {
        'id': 'm2',
        'conversation_id': 'c1',
        'role': 'assistant',
        'content': 'Merhaba!',
        'created_at': '2026-07-16T10:00:01Z',
        'metadata': {},
      },
    });

    final entity = model.toEntity();
    expect(entity.conversation.id, 'c1');
    expect(entity.userMessage.content, 'Selam');
    expect(entity.assistantMessage.content, 'Merhaba!');
  });
}
