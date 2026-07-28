import '../../domain/entities/ai_coach_entities.dart';

sealed class AiCoachState {
  const AiCoachState();
}

final class AiCoachInitial extends AiCoachState {
  const AiCoachInitial();
}

final class AiCoachLoading extends AiCoachState {
  const AiCoachLoading();
}

final class AiCoachLoaded extends AiCoachState {
  const AiCoachLoaded({
    required this.overview,
    required this.recommendations,
    required this.trends,
    required this.performance,
    required this.productivity,
  });

  final AiOverviewEntity overview;
  final List<AiRecommendationEntity> recommendations;
  final AiTrendsEntity trends;
  final AiPerformanceEntity performance;
  final AiProductivityEntity productivity;
}

final class AiCoachError extends AiCoachState {
  const AiCoachError(this.message);

  final String message;
}
