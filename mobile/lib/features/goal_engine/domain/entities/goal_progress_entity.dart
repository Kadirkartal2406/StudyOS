import 'goal_entity.dart';

class GoalProgressItemEntity {
  const GoalProgressItemEntity({
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
  });

  final String id;
  final String title;
  final GoalType goalType;
  final GoalPeriod period;
  final double progress;
  final double currentValue;
  final double targetValue;
  final double remaining;
  final double? etaDays;
  final GoalStatus status;
  final List<String> milestonesReached;
}

class GoalProgressEntity {
  const GoalProgressEntity({
    required this.items,
    this.activeCount = 0,
    this.completedCount = 0,
    this.averageProgress = 0,
  });

  final List<GoalProgressItemEntity> items;
  final int activeCount;
  final int completedCount;
  final double averageProgress;
}
