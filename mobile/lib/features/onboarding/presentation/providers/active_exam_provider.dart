import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../adaptive_planner/presentation/providers/planner_provider.dart';
import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../goal_engine/presentation/providers/goal_provider.dart';
import '../../../question_tracking/presentation/providers/question_tracking_provider.dart';
import '../../domain/entities/learning_profile_entity.dart';
import 'learning_profile_provider.dart';
import 'onboarding_provider.dart';

/// Sprint-3.1.A — Active Exam UI state (Primary'den bağımsız).
class ActiveExamState {
  const ActiveExamState({
    this.activeExamType,
    this.primaryExamType,
    this.availableExamTypes = const [],
    this.isChanging = false,
    this.error,
  });

  final String? activeExamType;
  final String? primaryExamType;
  final List<String> availableExamTypes;
  final bool isChanging;
  final String? error;

  ActiveExamState copyWith({
    String? activeExamType,
    String? primaryExamType,
    List<String>? availableExamTypes,
    bool? isChanging,
    String? error,
    bool clearError = false,
  }) {
    return ActiveExamState(
      activeExamType: activeExamType ?? this.activeExamType,
      primaryExamType: primaryExamType ?? this.primaryExamType,
      availableExamTypes: availableExamTypes ?? this.availableExamTypes,
      isChanging: isChanging ?? this.isChanging,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class ActiveExamController extends StateNotifier<ActiveExamState> {
  ActiveExamController(this._ref) : super(const ActiveExamState()) {
    _syncFromProfile();
    _ref.listen<AsyncValue<LearningProfileEntity>>(
      learningProfileProvider,
      (_, __) => _syncFromProfile(),
    );
  }

  final Ref _ref;

  void _syncFromProfile() {
    final profile = _ref.read(learningProfileProvider).valueOrNull;
    if (profile == null) return;
    state = state.copyWith(
      activeExamType: profile.activeExamType ?? profile.primaryExamType,
      primaryExamType: profile.primaryExamType,
      availableExamTypes: profile.switchableExamTypes,
      clearError: true,
    );
  }

  /// Active Exam değiştir — Primary dokunulmaz.
  Future<bool> setActiveExam(String examType) async {
    if (examType == state.activeExamType) return true;
    state = state.copyWith(isChanging: true, clearError: true);
    try {
      final profile = await _ref
          .read(learningProfileRepositoryProvider)
          .setActiveExam(examType);
      state = state.copyWith(
        activeExamType: profile.activeExamType ?? examType,
        primaryExamType: profile.primaryExamType,
        availableExamTypes: profile.switchableExamTypes,
        isChanging: false,
        clearError: true,
      );
      _invalidateScopedProviders();
      return true;
    } on AppException catch (e) {
      state = state.copyWith(isChanging: false, error: e.message);
      return false;
    } catch (_) {
      state = state.copyWith(
        isChanging: false,
        error: 'Active exam güncellenemedi',
      );
      return false;
    }
  }

  /// Profil yenilendikten sonra state'i senkronize et (Sınav Ekle sonrası).
  void refresh() => _syncFromProfile();

  void _invalidateScopedProviders() {
    _ref.invalidate(learningProfileProvider);
    _ref.invalidate(dashboardProvider);
    _ref.invalidate(goalProvider);
    _ref.invalidate(questionListProvider);
    _ref.invalidate(questionStatsProvider);
    _ref.invalidate(plannerProvider);
  }
}

final activeExamControllerProvider =
    StateNotifierProvider<ActiveExamController, ActiveExamState>((ref) {
  return ActiveExamController(ref);
});
