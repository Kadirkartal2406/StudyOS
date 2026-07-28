/// Yerel + (ileride) FCM bildirim sözleşmesi.
enum AppNotificationType {
  pomodoroStarted,
  pomodoroCompleted,
  longBreak,
  dailyGoalCompleted,
  studyReminder,
  streakWarning,
  widgetUpdated,
  goalMilestone,
  examMilestone,
  plannerReady,
  revisionDue,
  achievementUnlocked,
}

abstract class NotificationService {
  Future<void> init();

  Future<void> show({
    required AppNotificationType type,
    required String title,
    required String body,
  });

  Future<void> schedule({
    required AppNotificationType type,
    required String title,
    required String body,
    required Duration after,
    required int notificationId,
  });

  Future<void> cancel(int notificationId);

  Future<void> cancelAll();

  /// FCM token altyapısı — push gönderimi sonraki sprint.
  Future<String?> getFcmToken();
}
