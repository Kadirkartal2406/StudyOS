import '../core/platform/local_notification_service.dart';
import '../core/platform/notification_service.dart';

/// Pomodoro bitiş bildirimleri — LocalNotificationService üzerine ince sarmalayıcı.
/// Sprint-1.5 API'si korunur; Sprint-1.8 kanal/tip altyapısını kullanır.
class PomodoroNotificationService {
  PomodoroNotificationService({LocalNotificationService? notificationService})
      : _notifications = notificationService ?? LocalNotificationService();

  static const int _focusEndId = 1001;
  static const int _breakEndId = 1002;

  final LocalNotificationService _notifications;

  Future<void> init() => _notifications.init();

  Future<void> scheduleFocusEnd({required Duration after}) {
    return _notifications.schedule(
      type: AppNotificationType.pomodoroCompleted,
      title: 'Pomodoro tamamlandı',
      body: 'Odak süren bitti. Kısa bir mola zamanı!',
      after: after,
      notificationId: _focusEndId,
    );
  }

  Future<void> scheduleBreakEnd({required Duration after}) {
    return _notifications.schedule(
      type: AppNotificationType.longBreak,
      title: 'Mola bitti',
      body: 'Hazırsan bir sonraki odak oturumuna başla.',
      after: after,
      notificationId: _breakEndId,
    );
  }

  Future<void> showImmediate({
    required String title,
    required String body,
  }) {
    return _notifications.show(
      type: AppNotificationType.pomodoroCompleted,
      title: title,
      body: body,
    );
  }

  Future<void> cancelAll() async {
    await _notifications.cancel(_focusEndId);
    await _notifications.cancel(_breakEndId);
  }
}
