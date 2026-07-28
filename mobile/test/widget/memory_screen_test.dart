import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/memory/domain/entities/memory_entity.dart';
import 'package:studyos_mobile/features/memory/domain/repositories/memory_repository.dart';
import 'package:studyos_mobile/features/memory/presentation/providers/memory_provider.dart';
import 'package:studyos_mobile/features/memory/presentation/screens/memory_screen.dart';

class _FakeMemoryRepo implements MemoryRepository {
  @override
  Future<int> clearMemories() async => 0;

  @override
  Future<MemoryEntity> createMemory({
    required MemoryCategory category,
    required String content,
    double importance = 0.5,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<void> deleteMemory(String id) async {}

  @override
  Future<List<MemoryEntity>> exportMemories() async => [];

  @override
  Future<MemoryEntity> getMemory(String id) {
    throw UnimplementedError();
  }

  @override
  Future<MemorySettingsEntity> getSettings() async {
    return const MemorySettingsEntity(aiMemoryEnabled: true);
  }

  @override
  Future<List<MemoryEntity>> listMemories({bool activeOnly = true}) async {
    return [
      MemoryEntity(
        id: '1',
        category: MemoryCategory.weakSubject,
        content: 'Matematikte zorlanıyorum',
        importance: 0.8,
        source: 'ai_chat',
        accessCount: 1,
        isActive: true,
        createdAt: DateTime(2026, 7, 16),
        updatedAt: DateTime(2026, 7, 16),
      ),
    ];
  }

  @override
  Future<List<MemoryEntity>> search({
    String? query,
    MemoryCategory? category,
  }) async =>
      listMemories();

  @override
  Future<MemoryEntity> updateMemory({
    required String id,
    MemoryCategory? category,
    String? content,
    double? importance,
    bool? isActive,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<MemorySettingsEntity> updateSettings({required bool enabled}) async {
    return MemorySettingsEntity(aiMemoryEnabled: enabled);
  }
}

void main() {
  testWidgets('MemoryScreen lists memories and privacy controls',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          memoryRepositoryProvider.overrideWithValue(_FakeMemoryRepo()),
        ],
        child: const MaterialApp(home: MemoryScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('AI Bellek'), findsOneWidget);
    expect(find.text('Matematikte zorlanıyorum'), findsOneWidget);
    expect(find.text('AI bellek etkin'), findsOneWidget);
    expect(find.text('Dışa aktar'), findsOneWidget);
  });
}
