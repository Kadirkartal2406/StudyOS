import '../../domain/entities/study_resource_entity.dart';

sealed class StudyResourceState {
  const StudyResourceState();
}

class StudyResourceInitial extends StudyResourceState {
  const StudyResourceInitial();
}

class StudyResourceLoading extends StudyResourceState {
  const StudyResourceLoading();
}

class StudyResourceLoaded extends StudyResourceState {
  const StudyResourceLoaded({
    required this.items,
    this.statistics,
    this.errorMessage,
  });

  final List<StudyResourceEntity> items;
  final ResourceStatisticsEntity? statistics;
  final String? errorMessage;

  StudyResourceLoaded copyWith({
    List<StudyResourceEntity>? items,
    ResourceStatisticsEntity? statistics,
    String? errorMessage,
    bool clearError = false,
  }) {
    return StudyResourceLoaded(
      items: items ?? this.items,
      statistics: statistics ?? this.statistics,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class StudyResourceError extends StudyResourceState {
  const StudyResourceError(this.message);

  final String message;
}
