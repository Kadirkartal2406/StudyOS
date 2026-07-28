import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/notification_settings/data/models/notification_settings_model.dart';

void main() {
  test('NotificationSettingsModel.fromJson varsayılan ve alanları eşler', () {
    final model = NotificationSettingsModel.fromJson({
      'pomodoro_enabled': false,
      'long_break_enabled': true,
      'daily_reminder_enabled': true,
      'daily_goal_enabled': false,
      'streak_reminder_enabled': true,
      'achievement_notifications_enabled': false,
      'widget_auto_update_enabled': false,
      'quiet_hours_enabled': true,
      'quiet_hours_start': '22:00:00',
      'quiet_hours_end': '07:00:00',
      'has_fcm_token': true,
    });

    final entity = model.toEntity();
    expect(entity.pomodoroEnabled, isFalse);
    expect(entity.dailyGoalEnabled, isFalse);
    expect(entity.achievementNotificationsEnabled, isFalse);
    expect(entity.widgetAutoUpdateEnabled, isFalse);
    expect(entity.quietHoursEnabled, isTrue);
    expect(entity.hasFcmToken, isTrue);
    expect(entity.quietHoursStart, '22:00:00');
  });

  test('eksik alanlarda güvenli varsayılanlar', () {
    final model = NotificationSettingsModel.fromJson({});
    expect(model.pomodoroEnabled, isTrue);
    expect(model.hasFcmToken, isFalse);
    expect(model.widgetAutoUpdateEnabled, isTrue);
    expect(model.achievementNotificationsEnabled, isTrue);
  });
}
