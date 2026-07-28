import '../../domain/entities/memory_entity.dart';
import '../../domain/repositories/memory_repository.dart';
import '../datasources/memory_remote_datasource.dart';

class MemoryRepositoryImpl implements MemoryRepository {
  const MemoryRepositoryImpl(this._remote);

  final MemoryRemoteDatasource _remote;

  @override
  Future<List<MemoryEntity>> listMemories({bool activeOnly = true}) async {
    final models = await _remote.listMemories(activeOnly: activeOnly);
    return models.map((e) => e.toEntity()).toList();
  }

  @override
  Future<MemoryEntity> getMemory(String id) async {
    return (await _remote.getMemory(id)).toEntity();
  }

  @override
  Future<MemoryEntity> createMemory({
    required MemoryCategory category,
    required String content,
    double importance = 0.5,
  }) async {
    final model = await _remote.createMemory({
      'category': category.apiValue,
      'content': content,
      'importance': importance,
      'source': 'manual',
    });
    return model.toEntity();
  }

  @override
  Future<MemoryEntity> updateMemory({
    required String id,
    MemoryCategory? category,
    String? content,
    double? importance,
    bool? isActive,
  }) async {
    final body = <String, dynamic>{
      if (category != null) 'category': category.apiValue,
      if (content != null) 'content': content,
      if (importance != null) 'importance': importance,
      if (isActive != null) 'is_active': isActive,
    };
    return (await _remote.updateMemory(id, body)).toEntity();
  }

  @override
  Future<void> deleteMemory(String id) => _remote.deleteMemory(id);

  @override
  Future<List<MemoryEntity>> search({
    String? query,
    MemoryCategory? category,
  }) async {
    final models = await _remote.search({
      if (query != null && query.isNotEmpty) 'q': query,
      if (category != null) 'category': category.apiValue,
    });
    return models.map((e) => e.toEntity()).toList();
  }

  @override
  Future<MemorySettingsEntity> getSettings() async {
    return (await _remote.getSettings()).toEntity();
  }

  @override
  Future<MemorySettingsEntity> updateSettings({required bool enabled}) async {
    return (await _remote.updateSettings(enabled: enabled)).toEntity();
  }

  @override
  Future<List<MemoryEntity>> exportMemories() async {
    final models = await _remote.exportMemories();
    return models.map((e) => e.toEntity()).toList();
  }

  @override
  Future<int> clearMemories() => _remote.clearMemories();
}
