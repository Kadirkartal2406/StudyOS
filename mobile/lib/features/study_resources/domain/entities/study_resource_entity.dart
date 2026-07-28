enum ResourceType {
  youtube,
  pdf,
  website,
  book,
  document,
  note,
  video,
  audio,
  other;

  String get apiValue => name;

  String get label => switch (this) {
        ResourceType.youtube => 'YouTube',
        ResourceType.pdf => 'PDF',
        ResourceType.website => 'Web',
        ResourceType.book => 'Kitap',
        ResourceType.document => 'Doküman',
        ResourceType.note => 'Not',
        ResourceType.video => 'Video',
        ResourceType.audio => 'Ses',
        ResourceType.other => 'Diğer',
      };

  static ResourceType fromApi(String value) {
    for (final t in ResourceType.values) {
      if (t.name == value) return t;
    }
    return ResourceType.other;
  }
}

enum ResourceStatus {
  notStarted,
  inProgress,
  completed,
  archived;

  String get apiValue => switch (this) {
        ResourceStatus.notStarted => 'not_started',
        ResourceStatus.inProgress => 'in_progress',
        ResourceStatus.completed => 'completed',
        ResourceStatus.archived => 'archived',
      };

  String get label => switch (this) {
        ResourceStatus.notStarted => 'Başlanmadı',
        ResourceStatus.inProgress => 'Devam',
        ResourceStatus.completed => 'Tamamlandı',
        ResourceStatus.archived => 'Arşiv',
      };

  static ResourceStatus fromApi(String value) => switch (value) {
        'in_progress' => ResourceStatus.inProgress,
        'completed' => ResourceStatus.completed,
        'archived' => ResourceStatus.archived,
        _ => ResourceStatus.notStarted,
      };
}

class StudyResourceEntity {
  const StudyResourceEntity({
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
  final ResourceType resourceType;
  final String? url;
  final String? thumbnailUrl;
  final String? provider;
  final int? durationSeconds;
  final String? author;
  final ResourceStatus status;
  final int orderIndex;
  final DateTime? lastOpenedAt;
  final DateTime? completedAt;
  final Map<String, dynamic> metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  bool get isYoutube =>
      resourceType == ResourceType.youtube ||
      (url != null &&
          (url!.contains('youtube.com') || url!.contains('youtu.be')));
}

class ResourceStatisticsEntity {
  const ResourceStatisticsEntity({
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
}
