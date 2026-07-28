import '../../domain/entities/notification_settings_entity.dart';

class NotificationSettingsModel {
  const NotificationSettingsModel({
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

  factory NotificationSettingsModel.fromJson(Map<String, dynamic> json) {
    return NotificationSettingsModel(
      pomodoroEnabled: json['pomodoro_enabled'] as bool? ?? true,
      longBreakEnabled: json['long_break_enabled'] as bool? ?? true,
      dailyReminderEnabled: json['daily_reminder_enabled'] as bool? ?? true,
      dailyGoalEnabled: json['daily_goal_enabled'] as bool? ?? true,
      streakReminderEnabled: json['streak_reminder_enabled'] as bool? ?? true,
      achievementNotificationsEnabled:
          json['achievement_notifications_enabled'] as bool? ?? true,
      widgetAutoUpdateEnabled:
          json['widget_auto_update_enabled'] as bool? ?? true,
      reminderTime: json['reminder_time'] as String?,
      quietHoursEnabled: json['quiet_hours_enabled'] as bool? ?? false,
      quietHoursStart: json['quiet_hours_start'] as String?,
      quietHoursEnd: json['quiet_hours_end'] as String?,
      hasFcmToken: json['has_fcm_token'] as bool? ?? false,
    );
  }

  NotificationSettingsEntity toEntity() => NotificationSettingsEntity(
        pomodoroEnabled: pomodoroEnabled,
        longBreakEnabled: longBreakEnabled,
        dailyReminderEnabled: dailyReminderEnabled,
        dailyGoalEnabled: dailyGoalEnabled,
        streakReminderEnabled: streakReminderEnabled,
        achievementNotificationsEnabled: achievementNotificationsEnabled,
        widgetAutoUpdateEnabled: widgetAutoUpdateEnabled,
        reminderTime: reminderTime,
        quietHoursEnabled: quietHoursEnabled,
        quietHoursStart: quietHoursStart,
        quietHoursEnd: quietHoursEnd,
        hasFcmToken: hasFcmToken,
      );
}
