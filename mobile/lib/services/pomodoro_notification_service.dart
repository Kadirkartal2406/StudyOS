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

  Future<void> scheduleFocusEnd({required Duration after}) async {
    try {
      await _notifications.schedule(
        type: AppNotificationType.pomodoroCompleted,
        title: 'Pomodoro tamamlandı',
        body: 'Odak süren bitti. Kısa bir mola zamanı!',
        after: after,
        notificationId: _focusEndId,
      );
    } catch (_) {
      // Ignored to prevent state machine disruption
    }
  }

  Future<void> scheduleBreakEnd({required Duration after}) async {
    try {
      await _notifications.schedule(
        type: AppNotificationType.longBreak,
        title: 'Mola bitti',
        body: 'Hazırsan bir sonraki odak oturumuna başla.',
        after: after,
        notificationId: _breakEndId,
      );
    } catch (_) {
      // Ignored
    }
  }

  Future<void> showImmediate({
    required String title,
    required String body,
  }) async {
    try {
      await _notifications.show(
        type: AppNotificationType.pomodoroCompleted,
        title: title,
        body: body,
      );
    } catch (_) {
      // Ignored
    }
  }

  Future<void> cancelAll() async {
    try {
      await _notifications.cancel(_focusEndId);
      await _notifications.cancel(_breakEndId);
    } catch (_) {
      // Ignored
    }
  }
}
