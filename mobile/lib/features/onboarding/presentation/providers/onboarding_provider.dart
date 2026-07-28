import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/learning_profile_remote_datasource.dart';
import '../../data/repositories/learning_profile_repository.dart';
import '../../domain/entities/learning_profile_entity.dart';

final _learningRemoteProvider = Provider((ref) {
  return LearningProfileRemoteDatasource(ref.watch(dioClientProvider));
});

final learningProfileRepositoryProvider = Provider((ref) {
  return LearningProfileRepository(ref.watch(_learningRemoteProvider));
});

sealed class OnboardingUiState {
  const OnboardingUiState();
}

class OnboardingIdle extends OnboardingUiState {
  const OnboardingIdle();
}

class OnboardingLoading extends OnboardingUiState {
  const OnboardingLoading();
}

class OnboardingReady extends OnboardingUiState {
  const OnboardingReady(this.status);
  final OnboardingStatusEntity status;
}

class OnboardingError extends OnboardingUiState {
  const OnboardingError(this.message);
  final String message;
}

class OnboardingNotifier extends StateNotifier<OnboardingUiState> {
  OnboardingNotifier(this._repo) : super(const OnboardingIdle()) {
    refreshStatus();
  }

  final LearningProfileRepository _repo;

  Future<void> refreshStatus() async {
    state = const OnboardingLoading();
    try {
      final status = await _repo.status();
      state = OnboardingReady(status);
    } on AppException catch (e) {
      state = OnboardingError(e.message);
    } catch (_) {
      state = const OnboardingError('Onboarding durumu alınamadı');
    }
  }

  Future<LearningProfileEntity> complete(Map<String, dynamic> body) async {
    final profile = await _repo.complete(body);
    await refreshStatus();
    return profile;
  }
}

final onboardingProvider =
    StateNotifierProvider<OnboardingNotifier, OnboardingUiState>((ref) {
  return OnboardingNotifier(ref.watch(learningProfileRepositoryProvider));
});
