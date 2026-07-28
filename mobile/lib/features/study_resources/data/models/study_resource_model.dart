import '../../domain/entities/study_resource_entity.dart';

Map<String, dynamic> _asMap(Object? value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) {
    return value.map((k, v) => MapEntry(k.toString(), v));
  }
  return {};
}

class StudyResourceModel {
  const StudyResourceModel({
    required this.id,
    required this.title,
    required this.resourceType,
    required this.status,
    required this.orderIndex,
    required this.createdAt,
    required this.updatedAt,
    this.studyPlanId,
    this.description,
    this.url,
    this.thumbnailUrl,
    this.provider,
    this.durationSeconds,
    this.author,
    this.lastOpenedAt,
    this.completedAt,
    this.metadata = const {},
  });

  final String id;
  final String? studyPlanId;
  final String title;
  final String? description;
  final String resourceType;
  final String? url;
  final String? thumbnailUrl;
  final String? provider;
  final int? durationSeconds;
  final String? author;
  final String status;
  final int orderIndex;
  final DateTime? lastOpenedAt;
  final DateTime? completedAt;
  final Map<String, dynamic> metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory StudyResourceModel.fromJson(Map<String, dynamic> json) {
    return StudyResourceModel(
      id: json['id'] as String,
      studyPlanId: json['study_plan_id'] as String?,
      title: json['title'] as String,
      description: json['description'] as String?,
      resourceType: json['resource_type'] as String? ?? 'other',
      url: json['url'] as String?,
      thumbnailUrl: json['thumbnail_url'] as String?,
      provider: json['provider'] as String?,
      durationSeconds: json['duration_seconds'] as int?,
      author: json['author'] as String?,
      status: json['status'] as String? ?? 'not_started',
      orderIndex: json['order_index'] as int? ?? 0,
      lastOpenedAt: json['last_opened_at'] != null
          ? DateTime.parse(json['last_opened_at'] as String)
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      metadata: _asMap(json['metadata']),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  StudyResourceEntity toEntity() => StudyResourceEntity(
        id: id,
        studyPlanId: studyPlanId,
        title: title,
        description: description,
        resourceType: ResourceType.fromApi(resourceType),
        url: url,
        thumbnailUrl: thumbnailUrl,
        provider: provider,
        durationSeconds: durationSeconds,
        author: author,
        status: ResourceStatus.fromApi(status),
        orderIndex: orderIndex,
        lastOpenedAt: lastOpenedAt,
        completedAt: completedAt,
        metadata: metadata,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );
}

class ResourceStatisticsModel {
  const ResourceStatisticsModel({
    required this.totalCount,
    required this.completedCount,
    required this.inProgressCount,
    required this.todayCompletedCount,
    required this.todayOpenedCount,
    required this.totalVideoDurationSeconds,
    required this.completedVideoDurationSeconds,
    required this.byType,
  });

  final int totalCount;
  final int completedCount;
  final int inProgressCount;
  final int todayCompletedCount;
  final int todayOpenedCount;
  final int totalVideoDurationSeconds;
  final int completedVideoDurationSeconds;
  final Map<String, int> byType;

  factory ResourceStatisticsModel.fromJson(Map<String, dynamic> json) {
    final raw = json['by_type'];
    final byType = <String, int>{};
    if (raw is Map) {
      raw.forEach((k, v) {
        byType[k.toString()] = (v as num).toInt();
      });
    }
    return ResourceStatisticsModel(
      totalCount: json['total_count'] as int? ?? 0,
      completedCount: json['completed_count'] as int? ?? 0,
      inProgressCount: json['in_progress_count'] as int? ?? 0,
      todayCompletedCount: json['today_completed_count'] as int? ?? 0,
      todayOpenedCount: json['today_opened_count'] as int? ?? 0,
      totalVideoDurationSeconds:
          json['total_video_duration_seconds'] as int? ?? 0,
      completedVideoDurationSeconds:
          json['completed_video_duration_seconds'] as int? ?? 0,
      byType: byType,
    );
  }

  ResourceStatisticsEntity toEntity() => ResourceStatisticsEntity(
        totalCount: totalCount,
        completedCount: completedCount,
        inProgressCount: inProgressCount,
        todayCompletedCount: todayCompletedCount,
        todayOpenedCount: todayOpenedCount,
        totalVideoDurationSeconds: totalVideoDurationSeconds,
        completedVideoDurationSeconds: completedVideoDurationSeconds,
        byType: byType,
      );
}
