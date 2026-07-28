import '../entities/memory_entity.dart';

abstract class MemoryRepository {
  Future<List<MemoryEntity>> listMemories({bool activeOnly = true});
  Future<MemoryEntity> getMemory(String id);
  Future<MemoryEntity> createMemory({
    required MemoryCategory category,
    required String content,
    double importance = 0.5,
  });
  Future<MemoryEntity> updateMemory({
    required String id,
    MemoryCategory? category,
    String? content,
    double? importance,
    bool? isActive,
  });
  Future<void> deleteMemory(String id);
  Future<List<MemoryEntity>> search({
    String? query,
    MemoryCategory? category,
  });
  Future<MemorySettingsEntity> getSettings();
  Future<MemorySettingsEntity> updateSettings({required bool enabled});
  Future<List<MemoryEntity>> exportMemories();
  Future<int> clearMemories();
}
