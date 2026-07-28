/// Bildirim ayarları entity — Sprint-1.8 (+ Sprint-2.9 achievement toggle)
class NotificationSettingsEntity {
  const NotificationSettingsEntity({
    required this.pomodoroEnabled,
    required this.longBreakEnabled,
    required this.dailyReminderEnabled,
    required this.dailyGoalEnabled,
    required this.streakReminderEnabled,
    required this.widgetAutoUpdateEnabled,
    required this.quietHoursEnabled,
    required this.hasFcmToken,
    this.achievementNotificationsEnabled = true,
    this.reminderTime,
    this.quietHoursStart,
    this.quietHoursEnd,
  });

  final bool pomodoroEnabled;
  final bool longBreakEnabled;
  final bool dailyReminderEnabled;
  final bool dailyGoalEnabled;
  final bool streakReminderEnabled;
  final bool achievementNotificationsEnabled;
  final bool widgetAutoUpdateEnabled;
  final String? reminderTime;
  final bool quietHoursEnabled;
  final String? quietHoursStart;
  final String? quietHoursEnd;
  final bool hasFcmToken;

  NotificationSettingsEntity copyWith({
    bool? pomodoroEnabled,
    bool? longBreakEnabled,
    bool? dailyReminderEnabled,
    bool? dailyGoalEnabled,
    bool? streakReminderEnabled,
    bool? achievementNotificationsEnabled,
    bool? widgetAutoUpdateEnabled,
    String? reminderTime,
    bool? quietHoursEnabled,
    String? quietHoursStart,
    String? quietHoursEnd,
    bool? hasFcmToken,
  }) {
    return NotificationSettingsEntity(
      pomodoroEnabled: pomodoroEnabled ?? this.pomodoroEnabled,
      longBreakEnabled: longBreakEnabled ?? this.longBreakEnabled,
      dailyReminderEnabled: dailyReminderEnabled ?? this.dailyReminderEnabled,
      dailyGoalEnabled: dailyGoalEnabled ?? this.dailyGoalEnabled,
      streakReminderEnabled: streakReminderEnabled ?? this.streakReminderEnabled,
      achievementNotificationsEnabled: achievementNotificationsEnabled ??
          this.achievementNotificationsEnabled,
      widgetAutoUpdateEnabled:
          widgetAutoUpdateEnabled ?? this.widgetAutoUpdateEnabled,
      reminderTime: reminderTime ?? this.reminderTime,
      quietHoursEnabled: quietHoursEnabled ?? this.quietHoursEnabled,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      hasFcmToken: hasFcmToken ?? this.hasFcmToken,
    );
  }
}
