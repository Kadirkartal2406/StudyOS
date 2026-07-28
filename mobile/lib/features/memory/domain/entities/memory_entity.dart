enum MemoryCategory {
  studyHabit,
  goal,
  preference,
  weakSubject,
  strongSubject,
  schedule,
  conversation,
  motivation,
  exam,
  custom;

  String get apiValue => switch (this) {
        MemoryCategory.studyHabit => 'study_habit',
        MemoryCategory.goal => 'goal',
        MemoryCategory.preference => 'preference',
        MemoryCategory.weakSubject => 'weak_subject',
        MemoryCategory.strongSubject => 'strong_subject',
        MemoryCategory.schedule => 'schedule',
        MemoryCategory.conversation => 'conversation',
        MemoryCategory.motivation => 'motivation',
        MemoryCategory.exam => 'exam',
        MemoryCategory.custom => 'custom',
      };

  String get label => switch (this) {
        MemoryCategory.studyHabit => 'Çalışma alışkanlığı',
        MemoryCategory.goal => 'Hedef',
        MemoryCategory.preference => 'Tercih',
        MemoryCategory.weakSubject => 'Zayıf ders',
        MemoryCategory.strongSubject => 'Güçlü ders',
        MemoryCategory.schedule => 'Program',
        MemoryCategory.conversation => 'Sohbet',
        MemoryCategory.motivation => 'Motivasyon',
        MemoryCategory.exam => 'Sınav',
        MemoryCategory.custom => 'Özel',
      };

  static MemoryCategory fromApi(String value) => switch (value) {
        'study_habit' => MemoryCategory.studyHabit,
        'goal' => MemoryCategory.goal,
        'preference' => MemoryCategory.preference,
        'weak_subject' => MemoryCategory.weakSubject,
        'strong_subject' => MemoryCategory.strongSubject,
        'schedule' => MemoryCategory.schedule,
        'conversation' => MemoryCategory.conversation,
        'motivation' => MemoryCategory.motivation,
        'exam' => MemoryCategory.exam,
        _ => MemoryCategory.custom,
      };
}

class MemoryEntity {
  const MemoryEntity({
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
  final MemoryCategory category;
  final String content;
  final double importance;
  final String source;
  final int accessCount;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? lastAccessedAt;
  final Map<String, dynamic> metadata;
}

class MemorySettingsEntity {
  const MemorySettingsEntity({required this.aiMemoryEnabled});

  final bool aiMemoryEnabled;
}
