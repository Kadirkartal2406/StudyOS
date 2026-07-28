import '../entities/ai_coach_entities.dart';

abstract class AiCoachRepository {
  Future<AiOverviewEntity> getOverview();
  Future<List<AiRecommendationEntity>> getRecommendations();
  Future<AiTrendsEntity> getTrends();
  Future<AiPerformanceEntity> getPerformance();
  Future<AiProductivityEntity> getProductivity();
}
