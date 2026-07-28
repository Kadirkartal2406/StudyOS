import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/notification_service.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../data/datasources/planner_remote_datasource.dart';
import '../../data/repositories/planner_repository.dart';
import '../../domain/entities/planner_entity.dart';

sealed class PlannerUiState {
  const PlannerUiState();
}

class PlannerIdle extends PlannerUiState {
  const PlannerIdle();
}

class PlannerLoading extends PlannerUiState {
  const PlannerLoading();
}

class PlannerPreview extends PlannerUiState {
  const PlannerPreview(this.draft, {this.explanation, this.errorMessage});

  final PlannerDraftEntity draft;
  final String? explanation;
  final String? errorMessage;
}

class PlannerAccepted extends PlannerUiState {
  const PlannerAccepted(this.draft);

  final PlannerDraftEntity draft;
}

class PlannerError extends PlannerUiState {
  const PlannerError(this.message);

  final String message;
}

final _plannerRemoteProvider = Provider((ref) {
  return PlannerRemoteDatasource(ref.watch(dioClientProvider));
});

final plannerRepositoryProvider = Provider((ref) {
  return PlannerRepository(ref.watch(_plannerRemoteProvider));
});

class PlannerNotifier extends StateNotifier<PlannerUiState> {
  PlannerNotifier(this._repo, this._notifications) : super(const PlannerIdle());

  final PlannerRepository _repo;
  final NotificationService _notifications;

  Future<void> generate({
    required String targetExam,
    required double targetNet,
    required List<int> availableDays,
    required double availableHours,
  }) async {
    state = const PlannerLoading();
    try {
      final draft = await _repo.generate(
        targetExam: targetExam,
        targetNet: targetNet,
        availableDays: availableDays,
        availableHours: availableHours,
      );
      await _notifications.show(
        type: AppNotificationType.plannerReady,
        title: 'Plan hazır',
        body: 'Haftalık adaptive planın oluşturuldu. Önizlemeyi incele.',
      );
      state = PlannerPreview(draft);
    } on AppException catch (e) {
      state = PlannerError(e.message);
    } catch (_) {
      state = const PlannerError('Plan oluşturulamadı');
    }
  }

  Future<void> explain() async {
    final current = state;
    if (current is! PlannerPreview) return;
    try {
      final result = await _repo.explain(current.draft.id);
      state = PlannerPreview(current.draft, explanation: result.explanation);
    } on AppException catch (e) {
      state = PlannerPreview(current.draft, errorMessage: e.message);
    }
  }

  Future<bool> accept({bool force = false}) async {
    final current = state;
    if (current is! PlannerPreview) return false;
    try {
      final draft = await _repo.accept(current.draft.id, force: force);
      state = PlannerAccepted(draft);
      return true;
    } on ConflictException catch (e) {
      state = PlannerPreview(
        current.draft,
        errorMessage: '${e.message} — Zorla eklemek için “Yine de ekle”ye bas.',
      );
      return false;
    } on AppException catch (e) {
      state = PlannerPreview(current.draft, errorMessage: e.message);
      return false;
    }
  }

  void reset() => state = const PlannerIdle();
}

final plannerProvider =
    StateNotifierProvider<PlannerNotifier, PlannerUiState>((ref) {
  return PlannerNotifier(
    ref.watch(plannerRepositoryProvider),
    ref.watch(appNotificationServiceProvider),
  );
});
