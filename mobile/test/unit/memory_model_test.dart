import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/memory/data/models/memory_model.dart';
import 'package:studyos_mobile/features/memory/domain/entities/memory_entity.dart';

void main() {
  test('MemoryModel.fromJson maps fields', () {
    final model = MemoryModel.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'category': 'weak_subject',
      'content': 'Fizikte zorlanıyorum',
      'importance': 0.8,
      'source': 'ai_chat',
      'access_count': 2,
      'is_active': true,
      'created_at': '2026-07-16T10:00:00Z',
      'updated_at': '2026-07-16T10:00:00Z',
      'last_accessed_at': null,
      'metadata': {'embedding_ready': false},
    });

    final entity = model.toEntity();
    expect(entity.category, MemoryCategory.weakSubject);
    expect(entity.content, 'Fizikte zorlanıyorum');
    expect(entity.importance, 0.8);
    expect(entity.metadata['embedding_ready'], isFalse);
  });

  test('MemorySettingsModel.fromJson', () {
    final settings = MemorySettingsModel.fromJson({
      'ai_memory_enabled': false,
    });
    expect(settings.toEntity().aiMemoryEnabled, isFalse);
  });
}
