import '../../domain/entities/ai_coach_entities.dart';
import '../../domain/repositories/ai_coach_repository.dart';
import '../datasources/ai_coach_remote_datasource.dart';

class AiCoachRepositoryImpl implements AiCoachRepository {
  const AiCoachRepositoryImpl(this._remote);

  final AiCoachRemoteDatasource _remote;

  @override
  Future<AiOverviewEntity> getOverview() async {
    final model = await _remote.getOverview();
    return model.toEntity();
  }

  @override
  Future<List<AiRecommendationEntity>> getRecommendations() async {
    final models = await _remote.getRecommendations();
    return models.map((e) => e.toEntity()).toList();
  }

  @override
  Future<AiTrendsEntity> getTrends() async {
    final model = await _remote.getTrends();
    return model.toEntity();
  }

  @override
  Future<AiPerformanceEntity> getPerformance() async {
    final model = await _remote.getPerformance();
    return model.toEntity();
  }

  @override
  Future<AiProductivityEntity> getProductivity() async {
    final model = await _remote.getProductivity();
    return model.toEntity();
  }
}
