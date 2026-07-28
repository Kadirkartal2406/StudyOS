/// Platform yetenekleri — Android / iOS / WearOS / watchOS ortak sözleşme.
/// Sprint-1.8: gerçek implementasyonlar Android odaklı; iOS stub.
abstract class PlatformService {
  Future<bool> areNotificationsAllowed();

  Future<bool> requestNotificationPermission();

  /// Exact alarm (Android) — Pomodoro zamanlaması için.
  Future<bool> canScheduleExactAlarms();

  Future<void> openSystemNotificationSettings();
}
