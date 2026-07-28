import 'product_goal_type.dart';

/// Hedef türü — backend GoalType ile senkron.
enum GoalType {
  studyTime,
  pomodoro,
  question,
  subject,
  topic,
  custom;

  String get apiValue => switch (this) {
        GoalType.studyTime => 'study_time',
        GoalType.pomodoro => 'pomodoro',
        GoalType.question => 'question',
        GoalType.subject => 'subject',
        GoalType.topic => 'topic',
        GoalType.custom => 'custom',
      };

  static GoalType fromApi(String value) {
    return switch (value) {
      'study_time' => GoalType.studyTime,
      'pomodoro' => GoalType.pomodoro,
      'question' => GoalType.question,
      'subject' => GoalType.subject,
      'topic' => GoalType.topic,
      'custom' => GoalType.custom,
      _ => GoalType.custom,
    };
  }

  String get label => switch (this) {
        GoalType.studyTime => 'Çalışma Süresi',
        GoalType.pomodoro => 'Pomodoro',
        GoalType.question => 'Soru',
        GoalType.subject => 'Ders',
        GoalType.topic => 'Konu',
        GoalType.custom => 'Özel',
      };
}

enum GoalPeriod {
  daily,
  weekly,
  monthly,
  custom;

  String get apiValue => name;

  static GoalPeriod fromApi(String value) {
    for (final e in GoalPeriod.values) {
      if (e.name == value) return e;
    }
    return GoalPeriod.custom;
  }

  String get label => switch (this) {
        GoalPeriod.daily => 'Günlük',
        GoalPeriod.weekly => 'Haftalık',
        GoalPeriod.monthly => 'Aylık',
        GoalPeriod.custom => 'Özel',
      };
}

enum GoalPriority {
  low,
  medium,
  high,
  critical;

  String get apiValue => name;

  static GoalPriority fromApi(String value) {
    for (final e in GoalPriority.values) {
      if (e.name == value) return e;
    }
    return GoalPriority.medium;
  }

  String get label => switch (this) {
        GoalPriority.low => 'Düşük',
        GoalPriority.medium => 'Orta',
        GoalPriority.high => 'Yüksek',
        GoalPriority.critical => 'Kritik',
      };
}

enum GoalStatus {
  active,
  completed,
  paused,
  cancelled;

  String get apiValue => name;

  static GoalStatus fromApi(String value) {
    for (final e in GoalStatus.values) {
      if (e.name == value) return e;
    }
    return GoalStatus.active;
  }

  String get label => switch (this) {
        GoalStatus.active => 'Aktif',
        GoalStatus.completed => 'Tamamlandı',
        GoalStatus.paused => 'Duraklatıldı',
        GoalStatus.cancelled => 'İptal',
      };
}

class GoalEntity {
  const GoalEntity({
    required this.id,
    required this.userId,
    required this.title,
    required this.goalType,
    required this.targetValue,
    required this.currentValue,
    required this.progress,
    required this.priority,
    required this.period,
    required this.status,
    required this.startDate,
    required this.endDate,
    required this.milestonesReached,
    required this.remaining,
    required this.createdAt,
    required this.updatedAt,
    this.description,
    this.subject,
    this.topic,
    this.examType,
    this.productGoalType,
    this.completedAt,
    this.metadata = const {},
    this.etaDays,
    this.estimatedCompletion,
    this.progressSources = const [],
    this.progressLog = const [],
    this.whyCreated,
  });

  final String id;
  final String userId;
  final String title;
  final String? description;
  final GoalType goalType;
  final ProductGoalType? productGoalType;
  final double targetValue;
  final double currentValue;
  final double progress;
  final GoalPriority priority;
  final GoalPeriod period;
  final GoalStatus status;
  final String? subject;
  final String? topic;
  final String? examType;
  final DateTime startDate;
  final DateTime endDate;
  final DateTime? completedAt;
  final Map<String, dynamic> metadata;
  final List<String> milestonesReached;
  final double remaining;
  final double? etaDays;
  final String? estimatedCompletion;
  final List<String> progressSources;
  final List<GoalProgressLogEntry> progressLog;
  final String? whyCreated;
  final DateTime createdAt;
  final DateTime updatedAt;

  String get displayTypeLabel =>
      productGoalType?.label ?? goalType.label;
}

class GoalProgressLogEntry {
  const GoalProgressLogEntry({
    required this.at,
    required this.source,
    this.note,
    this.delta,
    this.value,
  });

  final String at;
  final String source;
  final String? note;
  final double? delta;
  final double? value;
}
