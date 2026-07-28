import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/notification_service.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../data/datasources/goal_remote_datasource.dart';
import '../../data/repositories/goal_repository_impl.dart';
import '../../domain/entities/goal_entity.dart';
import '../../domain/repositories/goal_repository.dart';
import 'goal_state.dart';

final _remoteProvider = Provider<GoalRemoteDatasource>((ref) {
  return GoalRemoteDatasource(ref.watch(dioClientProvider));
});

final goalRepositoryProvider = Provider<GoalRepository>((ref) {
  return GoalRepositoryImpl(ref.watch(_remoteProvider));
});

class GoalNotifier extends StateNotifier<GoalState> {
  GoalNotifier(
    this._repository,
    this._notifications,
  ) : super(const GoalInitial()) {
    load();
  }

  final GoalRepository _repository;
  final NotificationService _notifications;

  GoalFilterMode _filterMode = GoalFilterMode.active;

  Future<void> load() async {
    state = const GoalLoading();
    try {
      final goals = await _goalsForFilter(_filterMode);
      final progress = await _repository.getProgress();
      state = GoalLoaded(
        goals: goals,
        progress: progress,
        filterMode: _filterMode,
      );
      await _notifyNewMilestones(
        progress.items
            .map(
              (p) => (
                id: p.id,
                title: p.title,
                milestones: p.milestonesReached,
              ),
            )
            .followedBy(
              goals.map(
                (g) => (
                  id: g.id,
                  title: g.title,
                  milestones: g.milestonesReached,
                ),
              ),
            ),
      );
    } on AppException catch (e) {
      state = GoalError(e.message);
    } catch (_) {
      state = const GoalError('Hedefler yüklenemedi');
    }
  }

  Future<void> refresh() => load();

  Future<void> setFilter(GoalFilterMode mode) async {
    _filterMode = mode;
    await load();
  }

  Future<GoalEntity> create(Map<String, dynamic> body) async {
    final entity = await _repository.create(body);
    await load();
    return entity;
  }

  Future<GoalEntity> update(String id, Map<String, dynamic> body) async {
    final entity = await _repository.update(id, body);
    await load();
    return entity;
  }

  Future<void> delete(String id) async {
    await _repository.delete(id);
    await load();
  }

  Future<List<GoalEntity>> _goalsForFilter(GoalFilterMode mode) {
    return switch (mode) {
      GoalFilterMode.active => _repository.listActive(),
      GoalFilterMode.completed => _repository.listCompleted(),
      GoalFilterMode.progress => _repository.listActive(),
    };
  }

  Future<void> _notifyNewMilestones(
    Iterable<({String id, String title, List<String> milestones})> items,
  ) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final seen = <String>{};
      for (final item in items) {
        if (!seen.add(item.id)) continue;
        final key = 'goal_milestones_notified_${item.id}';
        final notified = prefs.getStringList(key) ?? <String>[];
        final fresh =
            item.milestones.where((m) => !notified.contains(m)).toList();
        for (final milestone in fresh) {
          await _notifications.show(
            type: AppNotificationType.goalMilestone,
            title: 'Hedef kilometre taşı',
            body: '${item.title}: %$milestone tamamlandı!',
          );
        }
        if (fresh.isNotEmpty) {
          await prefs.setStringList(key, [...notified, ...fresh]);
        }
      }
    } catch (_) {
      // Bildirim hatası UI'yi bozmamalı.
    }
  }
}

final goalProvider = StateNotifierProvider<GoalNotifier, GoalState>((ref) {
  return GoalNotifier(
    ref.watch(goalRepositoryProvider),
    ref.watch(appNotificationServiceProvider),
  );
});

final goalDetailProvider =
    FutureProvider.family<GoalEntity, String>((ref, id) async {
  return ref.watch(goalRepositoryProvider).getById(id);
});
