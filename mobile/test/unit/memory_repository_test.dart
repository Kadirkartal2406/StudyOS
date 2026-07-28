import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/memory/data/datasources/memory_remote_datasource.dart';
import 'package:studyos_mobile/features/memory/data/models/memory_model.dart';
import 'package:studyos_mobile/features/memory/data/repositories/memory_repository_impl.dart';
import 'package:studyos_mobile/features/memory/domain/entities/memory_entity.dart';

class _MockMemoryRemote extends Mock implements MemoryRemoteDatasource {}

MemoryModel _model() {
  return MemoryModel(
    id: 'm1',
    category: 'exam',
    content: 'YKS hazırlığı',
    importance: 0.85,
    source: 'manual',
    accessCount: 0,
    isActive: true,
    createdAt: DateTime(2026, 7, 16),
    updatedAt: DateTime(2026, 7, 16),
    metadata: const {'embedding_ready': false},
  );
}

void main() {
  late _MockMemoryRemote remote;
  late MemoryRepositoryImpl repo;

  setUpAll(() {
    registerFallbackValue(<String, dynamic>{});
  });

  setUp(() {
    remote = _MockMemoryRemote();
    repo = MemoryRepositoryImpl(remote);
  });

  test('listMemories maps models to entities', () async {
    when(() => remote.listMemories(activeOnly: any(named: 'activeOnly')))
        .thenAnswer((_) async => [_model()]);

    final items = await repo.listMemories();
    expect(items, hasLength(1));
    expect(items.first.category, MemoryCategory.exam);
  });

  test('createMemory builds body', () async {
    when(() => remote.createMemory(any())).thenAnswer((_) async => _model());

    final entity = await repo.createMemory(
      category: MemoryCategory.exam,
      content: 'YKS hazırlığı',
      importance: 0.85,
    );
    expect(entity.id, 'm1');
    final body = verify(() => remote.createMemory(captureAny())).captured.single
        as Map<String, dynamic>;
    expect(body['category'], 'exam');
    expect(body['source'], 'manual');
  });
}
