import '../../domain/entities/goal_entity.dart';
import '../../domain/entities/goal_progress_entity.dart';
import '../../domain/entities/product_goal_type.dart';

class GoalModel {
  const GoalModel({
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
  final String goalType;
  final String? productGoalType;
  final double targetValue;
  final double currentValue;
  final double progress;
  final String priority;
  final String period;
  final String status;
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
  final List<Map<String, dynamic>> progressLog;
  final String? whyCreated;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory GoalModel.fromJson(Map<String, dynamic> json) {
    final logRaw = json['progress_log'] as List<dynamic>? ?? [];
    return GoalModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      goalType: json['goal_type'] as String,
      productGoalType: json['product_goal_type'] as String?,
      targetValue: _toDouble(json['target_value']),
      currentValue: _toDouble(json['current_value']),
      progress: _toDouble(json['progress']),
      priority: json['priority'] as String? ?? 'medium',
      period: json['period'] as String,
      status: json['status'] as String? ?? 'active',
      subject: json['subject'] as String?,
      topic: json['topic'] as String?,
      examType: json['exam_type'] as String?,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      completedAt: json['completed_at'] == null
          ? null
          : DateTime.parse(json['completed_at'] as String),
      metadata: json['metadata'] is Map
          ? Map<String, dynamic>.from(json['metadata'] as Map)
          : const {},
      milestonesReached: (json['milestones_reached'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
      remaining: _toDouble(json['remaining']),
      etaDays: json['eta_days'] == null ? null : _toDouble(json['eta_days']),
      estimatedCompletion: json['estimated_completion'] as String?,
      progressSources: (json['progress_sources'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
      progressLog: logRaw
          .whereType<Map>()
          .map((e) => Map<String, dynamic>.from(e))
          .toList(),
      whyCreated: json['why_created'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  GoalEntity toEntity() => GoalEntity(
        id: id,
        userId: userId,
        title: title,
        description: description,
        goalType: GoalType.fromApi(goalType),
        productGoalType: ProductGoalType.fromApi(productGoalType),
        targetValue: targetValue,
        currentValue: currentValue,
        progress: progress,
        priority: GoalPriority.fromApi(priority),
        period: GoalPeriod.fromApi(period),
        status: GoalStatus.fromApi(status),
        subject: subject,
        topic: topic,
        examType: examType,
        startDate: startDate,
        endDate: endDate,
        completedAt: completedAt,
        metadata: metadata,
        milestonesReached: milestonesReached,
        remaining: remaining,
        etaDays: etaDays,
        estimatedCompletion: estimatedCompletion,
        progressSources: progressSources,
        progressLog: progressLog
            .map(
              (e) => GoalProgressLogEntry(
                at: e['at']?.toString() ?? '',
                source: e['source']?.toString() ?? '',
                note: e['note']?.toString(),
                delta: e['delta'] == null ? null : _toDouble(e['delta']),
                value: e['value'] == null ? null : _toDouble(e['value']),
              ),
            )
            .toList(),
        whyCreated: whyCreated,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );
}

class GoalProgressItemModel {
  const GoalProgressItemModel({
    required this.id,
    required this.title,
    required this.goalType,
    required this.period,
    required this.progress,
    required this.currentValue,
    required this.targetValue,
    required this.remaining,
    required this.status,
    required this.milestonesReached,
    this.etaDays,
    this.estimatedCompletion,
    this.productGoalType,
  });

  final String id;
  final String title;
  final String goalType;
  final String? productGoalType;
  final String period;
  final double progress;
  final double currentValue;
  final double targetValue;
  final double remaining;
  final double? etaDays;
  final String? estimatedCompletion;
  final String status;
  final List<String> milestonesReached;

  factory GoalProgressItemModel.fromJson(Map<String, dynamic> json) {
    return GoalProgressItemModel(
      id: json['id'] as String,
      title: json['title'] as String,
      goalType: json['goal_type'] as String,
      productGoalType: json['product_goal_type'] as String?,
      period: json['period'] as String,
      progress: _toDouble(json['progress']),
      currentValue: _toDouble(json['current_value']),
      targetValue: _toDouble(json['target_value']),
      remaining: _toDouble(json['remaining']),
      etaDays: json['eta_days'] == null ? null : _toDouble(json['eta_days']),
      estimatedCompletion: json['estimated_completion'] as String?,
      status: json['status'] as String? ?? 'active',
      milestonesReached: (json['milestones_reached'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
    );
  }

  GoalProgressItemEntity toEntity() => GoalProgressItemEntity(
        id: id,
        title: title,
        goalType: GoalType.fromApi(goalType),
        period: GoalPeriod.fromApi(period),
        progress: progress,
        currentValue: currentValue,
        targetValue: targetValue,
        remaining: remaining,
        etaDays: etaDays,
        status: GoalStatus.fromApi(status),
        milestonesReached: milestonesReached,
      );
}

class GoalProgressModel {
  const GoalProgressModel({
    required this.items,
    this.activeCount = 0,
    this.completedCount = 0,
    this.averageProgress = 0,
  });

  final List<GoalProgressItemModel> items;
  final int activeCount;
  final int completedCount;
  final double averageProgress;

  factory GoalProgressModel.fromJson(Map<String, dynamic> json) {
    final itemsJson = json['items'] as List<dynamic>? ?? [];
    return GoalProgressModel(
      items: itemsJson
          .map(
            (e) => GoalProgressItemModel.fromJson(e as Map<String, dynamic>),
          )
          .toList(),
      activeCount: json['active_count'] as int? ?? 0,
      completedCount: json['completed_count'] as int? ?? 0,
      averageProgress: _toDouble(json['average_progress']),
    );
  }

  GoalProgressEntity toEntity() => GoalProgressEntity(
        items: items.map((e) => e.toEntity()).toList(),
        activeCount: activeCount,
        completedCount: completedCount,
        averageProgress: averageProgress,
      );
}

class GoalExplainModel {
  const GoalExplainModel({
    required this.goalId,
    required this.explanation,
    required this.whyProgressed,
    required this.whyStalled,
    required this.howToComplete,
    required this.title,
    required this.progress,
    this.provider,
    this.usedFallback = false,
  });

  final String goalId;
  final String explanation;
  final String whyProgressed;
  final String whyStalled;
  final String howToComplete;
  final String title;
  final double progress;
  final String? provider;
  final bool usedFallback;

  factory GoalExplainModel.fromJson(Map<String, dynamic> json) {
    return GoalExplainModel(
      goalId: json['goal_id'] as String,
      explanation: json['explanation'] as String? ?? '',
      whyProgressed: json['why_progressed'] as String? ?? '',
      whyStalled: json['why_stalled'] as String? ?? '',
      howToComplete: json['how_to_complete'] as String? ?? '',
      title: json['title'] as String? ?? '',
      progress: _toDouble(json['progress']),
      provider: json['provider'] as String?,
      usedFallback: json['used_fallback'] as bool? ?? false,
    );
  }
}

double _toDouble(Object? value) {
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? 0;
  return 0;
}
