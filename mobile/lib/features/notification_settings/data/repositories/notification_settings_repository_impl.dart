import '../../domain/entities/notification_settings_entity.dart';
import '../../domain/repositories/notification_settings_repository.dart';
import '../datasources/notification_settings_remote_datasource.dart';

class NotificationSettingsRepositoryImpl
    implements NotificationSettingsRepository {
  const NotificationSettingsRepositoryImpl(this._remote);

  final NotificationSettingsRemoteDatasource _remote;

  @override
  Future<NotificationSettingsEntity> getSettings() async {
    final model = await _remote.getSettings();
    return model.toEntity();
  }

  @override
  Future<NotificationSettingsEntity> updateSettings(
    Map<String, dynamic> body,
  ) async {
    final model = await _remote.updateSettings(body);
    return model.toEntity();
  }

  @override
  Future<NotificationSettingsEntity> updateFcmToken(String token) async {
    final model = await _remote.updateFcmToken(token);
    return model.toEntity();
  }
}
