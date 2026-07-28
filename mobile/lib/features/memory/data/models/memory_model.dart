import '../../domain/entities/memory_entity.dart';

Map<String, dynamic> _asStringKeyMap(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) {
    return value.map((key, val) => MapEntry(key.toString(), val));
  }
  return {};
}

class MemoryModel {
  const MemoryModel({
    required this.id,
    required this.category,
    required this.content,
    required this.importance,
    required this.source,
    required this.accessCount,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.lastAccessedAt,
    this.metadata = const {},
  });

  final String id;
  final String category;
  final String content;
  final double importance;
  final String source;
  final int accessCount;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastAccessedAt;
  final Map<String, dynamic> metadata;

  factory MemoryModel.fromJson(Map<String, dynamic> json) {
    return MemoryModel(
      id: json['id'] as String,
      category: json['category'] as String,
      content: json['content'] as String,
      importance: (json['importance'] as num).toDouble(),
      source: json['source'] as String? ?? 'manual',
      accessCount: json['access_count'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      lastAccessedAt: json['last_accessed_at'] != null
          ? DateTime.parse(json['last_accessed_at'] as String)
          : null,
      metadata: _asStringKeyMap(json['metadata']),
    );
  }

  MemoryEntity toEntity() => MemoryEntity(
        id: id,
        category: MemoryCategory.fromApi(category),
        content: content,
        importance: importance,
        source: source,
        accessCount: accessCount,
        isActive: isActive,
        createdAt: createdAt,
        updatedAt: updatedAt,
        lastAccessedAt: lastAccessedAt,
        metadata: metadata,
      );
}

class MemorySettingsModel {
  const MemorySettingsModel({required this.aiMemoryEnabled});

  final bool aiMemoryEnabled;

  factory MemorySettingsModel.fromJson(Map<String, dynamic> json) {
    return MemorySettingsModel(
      aiMemoryEnabled: json['ai_memory_enabled'] as bool? ?? true,
    );
  }

  MemorySettingsEntity toEntity() =>
      MemorySettingsEntity(aiMemoryEnabled: aiMemoryEnabled);
}
