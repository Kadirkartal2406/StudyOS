import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/notification_service.dart';
import '../../../notification_settings/presentation/providers/notification_settings_provider.dart';
import '../../data/datasources/achievement_remote_datasource.dart';
import '../../data/repositories/achievement_repository.dart';
import '../../domain/entities/achievement_entity.dart';

sealed class AchievementUiState {
  const AchievementUiState();
}

class AchievementLoading extends AchievementUiState {
  const AchievementLoading();
}

class AchievementLoaded extends AchievementUiState {
  const AchievementLoaded({
    required this.progress,
    required this.unlocked,
    this.explanation,
    this.errorMessage,
  });

  final List<AchievementEntity> progress;
  final List<AchievementEntity> unlocked;
  final String? explanation;
  final String? errorMessage;
}

class AchievementError extends AchievementUiState {
  const AchievementError(this.message);

  final String message;
}

final _achievementRemoteProvider = Provider((ref) {
  return AchievementRemoteDatasource(ref.watch(dioClientProvider));
});

final achievementRepositoryProvider = Provider((ref) {
  return AchievementRepository(ref.watch(_achievementRemoteProvider));
});

class AchievementNotifier extends StateNotifier<AchievementUiState> {
  AchievementNotifier(this._repo, this._notifications, this._ref)
      : super(const AchievementLoading()) {
    load();
  }

  final AchievementRepository _repo;
  final NotificationService _notifications;
  final Ref _ref;

  Future<void> load() async {
    state = const AchievementLoading();
    try {
      final progress = await _repo.listProgress();
      final unlocked = await _repo.listUnlocked();
      state = AchievementLoaded(progress: progress, unlocked: unlocked);
    } on AppException catch (e) {
      state = AchievementError(e.message);
    } catch (_) {
      state = const AchievementError('Rozetler yüklenemedi');
    }
  }

  Future<void> checkAndNotify() async {
    try {
      final newly = await _repo.check();
      if (newly.isNotEmpty && _achievementNotifyAllowed()) {
        await _notifications.show(
          type: AppNotificationType.achievementUnlocked,
          title: 'Yeni rozet!',
          body: newly.length == 1
              ? newly.first.title
              : '${newly.length} yeni rozet açıldı',
        );
      }
      await load();
    } on AppException catch (e) {
      if (state is AchievementLoaded) {
        final cur = state as AchievementLoaded;
        state = AchievementLoaded(
          progress: cur.progress,
          unlocked: cur.unlocked,
          errorMessage: e.message,
        );
      }
    }
  }

  bool _achievementNotifyAllowed() {
    final settings = _ref.read(notificationSettingsProvider);
    if (settings is NotificationSettingsLoaded) {
      return settings.settings.achievementNotificationsEnabled;
    }
    return true;
  }

  Future<void> explain(String id) async {
    final current = state;
    if (current is! AchievementLoaded) return;
    try {
      final result = await _repo.explain(id);
      state = AchievementLoaded(
        progress: current.progress,
        unlocked: current.unlocked,
        explanation: result.explanation,
      );
    } on AppException catch (e) {
      state = AchievementLoaded(
        progress: current.progress,
        unlocked: current.unlocked,
        errorMessage: e.message,
      );
    }
  }
}

final achievementProvider =
    StateNotifierProvider<AchievementNotifier, AchievementUiState>((ref) {
  return AchievementNotifier(
    ref.watch(achievementRepositoryProvider),
    ref.watch(appNotificationServiceProvider),
    ref,
  );
});
