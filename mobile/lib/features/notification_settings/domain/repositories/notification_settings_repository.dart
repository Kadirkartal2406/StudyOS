import '../entities/notification_settings_entity.dart';

abstract class NotificationSettingsRepository {
  Future<NotificationSettingsEntity> getSettings();

  Future<NotificationSettingsEntity> updateSettings(
    Map<String, dynamic> body,
  );

  Future<NotificationSettingsEntity> updateFcmToken(String token);
}
