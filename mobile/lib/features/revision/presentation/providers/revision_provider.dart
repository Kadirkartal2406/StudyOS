import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/notification_service.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../data/datasources/revision_remote_datasource.dart';
import '../../data/repositories/revision_repository.dart';
import '../../domain/entities/revision_entity.dart';

sealed class RevisionUiState {
  const RevisionUiState();
}

class RevisionLoading extends RevisionUiState {
  const RevisionLoading();
}

class RevisionLoaded extends RevisionUiState {
  const RevisionLoaded({
    required this.today,
    required this.stats,
    this.explanation,
    this.errorMessage,
  });

  final List<RevisionItemEntity> today;
  final RevisionStatisticsEntity stats;
  final String? explanation;
  final String? errorMessage;
}

class RevisionError extends RevisionUiState {
  const RevisionError(this.message);

  final String message;
}

final _revisionRemoteProvider = Provider((ref) {
  return RevisionRemoteDatasource(ref.watch(dioClientProvider));
});

final revisionRepositoryProvider = Provider((ref) {
  return RevisionRepository(ref.watch(_revisionRemoteProvider));
});

class RevisionNotifier extends StateNotifier<RevisionUiState> {
  RevisionNotifier(this._repo, this._notifications)
      : super(const RevisionLoading()) {
    load();
  }

  final RevisionRepository _repo;
  final NotificationService _notifications;

  Future<void> load() async {
    state = const RevisionLoading();
    try {
      final today = await _repo.listToday();
      final stats = await _repo.statistics();
      if (stats.dueToday > 0) {
        await _notifications.show(
          type: AppNotificationType.revisionDue,
          title: 'Tekrar zamanı',
          body: 'Bugün ${stats.dueToday} tekrar kartın var.',
        );
      }
      state = RevisionLoaded(today: today, stats: stats);
    } on AppException catch (e) {
      state = RevisionError(e.message);
    } catch (_) {
      state = const RevisionError('Tekrarlar yüklenemedi');
    }
  }

  Future<void> generate() async {
    final current = state;
    try {
      final result = await _repo.generate();
      await load();
      if (current is RevisionLoaded) {
        // load() already set state
      }
      if (result.created.isNotEmpty) {
        await _notifications.show(
          type: AppNotificationType.revisionDue,
          title: 'Tekrar kuyruğu hazır',
          body: result.message,
        );
      }
    } on AppException catch (e) {
      if (state is RevisionLoaded) {
        final loaded = state as RevisionLoaded;
        state = RevisionLoaded(
          today: loaded.today,
          stats: loaded.stats,
          errorMessage: e.message,
        );
      } else {
        state = RevisionError(e.message);
      }
    }
  }

  Future<void> review(String id, String grade) async {
    try {
      await _repo.review(id, grade);
      await load();
    } on AppException catch (e) {
      if (state is RevisionLoaded) {
        final loaded = state as RevisionLoaded;
        state = RevisionLoaded(
          today: loaded.today,
          stats: loaded.stats,
          errorMessage: e.message,
        );
      }
    }
  }

  Future<void> skip(String id) async {
    try {
      await _repo.skip(id);
      await load();
    } on AppException catch (_) {
      await load();
    }
  }

  Future<void> postpone(String id) async {
    try {
      await _repo.postpone(id);
      await load();
    } on AppException catch (_) {
      await load();
    }
  }

  Future<void> explain(String id) async {
    final current = state;
    if (current is! RevisionLoaded) return;
    try {
      final result = await _repo.explain(id);
      state = RevisionLoaded(
        today: current.today,
        stats: current.stats,
        explanation: result.explanation,
      );
    } on AppException catch (e) {
      state = RevisionLoaded(
        today: current.today,
        stats: current.stats,
        errorMessage: e.message,
      );
    }
  }

  Future<void> addManual({
    required String title,
    required String subject,
    String? reason,
  }) async {
    try {
      await _repo.create(
        title: title,
        subject: subject,
        reason: reason,
      );
      await load();
    } on AppException catch (e) {
      if (state is RevisionLoaded) {
        final loaded = state as RevisionLoaded;
        state = RevisionLoaded(
          today: loaded.today,
          stats: loaded.stats,
          errorMessage: e.message,
        );
      }
    }
  }
}

final revisionProvider =
    StateNotifierProvider<RevisionNotifier, RevisionUiState>((ref) {
  return RevisionNotifier(
    ref.watch(revisionRepositoryProvider),
    ref.watch(appNotificationServiceProvider),
  );
});
