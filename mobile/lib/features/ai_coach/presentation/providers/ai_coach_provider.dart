import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/ai_coach_remote_datasource.dart';
import '../../data/repositories/ai_coach_repository_impl.dart';
import '../../domain/repositories/ai_coach_repository.dart';
import 'ai_coach_state.dart';

final _remoteProvider = Provider<AiCoachRemoteDatasource>((ref) {
  return AiCoachRemoteDatasource(ref.watch(dioClientProvider));
});

final aiCoachRepositoryProvider = Provider<AiCoachRepository>((ref) {
  return AiCoachRepositoryImpl(ref.watch(_remoteProvider));
});

class AiCoachNotifier extends StateNotifier<AiCoachState> {
  AiCoachNotifier(this._repository) : super(const AiCoachInitial()) {
    load();
  }

  final AiCoachRepository _repository;

  Future<void> load() async {
    state = const AiCoachLoading();
    try {
      final overview = await _repository.getOverview();
      final recommendations = await _repository.getRecommendations();
      final trends = await _repository.getTrends();
      final performance = await _repository.getPerformance();
      final productivity = await _repository.getProductivity();
      state = AiCoachLoaded(
        overview: overview,
        recommendations: recommendations,
        trends: trends,
        performance: performance,
        productivity: productivity,
      );
    } on AppException catch (e) {
      state = AiCoachError(e.message);
    } catch (_) {
      state = const AiCoachError('AI önerileri yüklenemedi');
    }
  }
}

final aiCoachProvider =
    StateNotifierProvider<AiCoachNotifier, AiCoachState>((ref) {
  return AiCoachNotifier(ref.watch(aiCoachRepositoryProvider));
});
