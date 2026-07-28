import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../../../core/platform/platform_service.dart';
import '../../data/datasources/notification_settings_remote_datasource.dart';
import '../../data/repositories/notification_settings_repository_impl.dart';
import '../../domain/entities/notification_settings_entity.dart';
import '../../domain/repositories/notification_settings_repository.dart';

export '../../../../core/platform/platform_providers.dart'
    show appNotificationServiceProvider, platformServiceProvider;

final notificationSettingsRepositoryProvider =
    Provider<NotificationSettingsRepository>((ref) {
  return NotificationSettingsRepositoryImpl(
    NotificationSettingsRemoteDatasource(ref.watch(dioClientProvider)),
  );
});

sealed class NotificationSettingsState {
  const NotificationSettingsState();
}

class NotificationSettingsInitial extends NotificationSettingsState {
  const NotificationSettingsInitial();
}

class NotificationSettingsLoading extends NotificationSettingsState {
  const NotificationSettingsLoading();
}

class NotificationSettingsLoaded extends NotificationSettingsState {
  const NotificationSettingsLoaded(this.settings, {this.notificationsAllowed});
  final NotificationSettingsEntity settings;
  final bool? notificationsAllowed;
}

class NotificationSettingsError extends NotificationSettingsState {
  const NotificationSettingsError(this.message);
  final String message;
}

class NotificationSettingsNotifier
    extends StateNotifier<NotificationSettingsState> {
  NotificationSettingsNotifier(this._repo, this._platform)
      : super(const NotificationSettingsInitial());

  final NotificationSettingsRepository _repo;
  final PlatformService _platform;

  Future<void> load() async {
    state = const NotificationSettingsLoading();
    try {
      final settings = await _repo.getSettings();
      final allowed = await _platform.areNotificationsAllowed();
      state = NotificationSettingsLoaded(
        settings,
        notificationsAllowed: allowed,
      );
    } on AppException catch (e) {
      state = NotificationSettingsError(e.message);
    } catch (_) {
      state = const NotificationSettingsError('Ayarlar yüklenemedi');
    }
  }

  Future<void> toggle(String field, bool value) async {
    final current = state;
    if (current is! NotificationSettingsLoaded) return;
    try {
      final updated = await _repo.updateSettings({field: value});
      state = NotificationSettingsLoaded(
        updated,
        notificationsAllowed: current.notificationsAllowed,
      );
    } on AppException catch (e) {
      state = NotificationSettingsError(e.message);
    }
  }

  Future<void> syncFcmTokenStub(String token) async {
    final current = state;
    if (current is! NotificationSettingsLoaded) return;
    final updated = await _repo.updateFcmToken(token);
    state = NotificationSettingsLoaded(
      updated,
      notificationsAllowed: current.notificationsAllowed,
    );
  }
}

final notificationSettingsProvider = StateNotifierProvider<
    NotificationSettingsNotifier, NotificationSettingsState>((ref) {
  return NotificationSettingsNotifier(
    ref.watch(notificationSettingsRepositoryProvider),
    ref.watch(platformServiceProvider),
  );
});
