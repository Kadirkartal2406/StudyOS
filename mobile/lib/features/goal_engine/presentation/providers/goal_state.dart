import '../../domain/entities/goal_entity.dart';
import '../../domain/entities/goal_progress_entity.dart';

enum GoalFilterMode { active, progress, completed }

sealed class GoalState {
  const GoalState();
}

final class GoalInitial extends GoalState {
  const GoalInitial();
}

final class GoalLoading extends GoalState {
  const GoalLoading();
}

final class GoalLoaded extends GoalState {
  const GoalLoaded({
    required this.goals,
    required this.progress,
    this.filterMode = GoalFilterMode.active,
  });

  final List<GoalEntity> goals;
  final GoalProgressEntity progress;
  final GoalFilterMode filterMode;

  GoalLoaded copyWith({
    List<GoalEntity>? goals,
    GoalProgressEntity? progress,
    GoalFilterMode? filterMode,
  }) {
    return GoalLoaded(
      goals: goals ?? this.goals,
      progress: progress ?? this.progress,
      filterMode: filterMode ?? this.filterMode,
    );
  }
}

final class GoalError extends GoalState {
  const GoalError(this.message);

  final String message;
}
