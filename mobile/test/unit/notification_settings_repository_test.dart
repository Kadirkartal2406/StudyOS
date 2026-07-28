import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/notification_settings/data/datasources/notification_settings_remote_datasource.dart';
import 'package:studyos_mobile/features/notification_settings/data/models/notification_settings_model.dart';
import 'package:studyos_mobile/features/notification_settings/data/repositories/notification_settings_repository_impl.dart';

class _MockRemote extends Mock implements NotificationSettingsRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late NotificationSettingsRepositoryImpl repo;

  setUp(() {
    remote = _MockRemote();
    repo = NotificationSettingsRepositoryImpl(remote);
  });

  const model = NotificationSettingsModel(
    pomodoroEnabled: true,
    longBreakEnabled: true,
    dailyReminderEnabled: true,
    dailyGoalEnabled: true,
    streakReminderEnabled: true,
    widgetAutoUpdateEnabled: true,
    quietHoursEnabled: false,
    hasFcmToken: false,
  );

  test('getSettings entity döner', () async {
    when(() => remote.getSettings()).thenAnswer((_) async => model);
    final entity = await repo.getSettings();
    expect(entity.pomodoroEnabled, isTrue);
    verify(() => remote.getSettings()).called(1);
  });

  test('updateSettings body ile çağırır', () async {
    when(() => remote.updateSettings(any())).thenAnswer((_) async => model);
    await repo.updateSettings({'pomodoro_enabled': false});
    verify(() => remote.updateSettings({'pomodoro_enabled': false})).called(1);
  });

  test('updateFcmToken entity döner', () async {
    when(() => remote.updateFcmToken(any())).thenAnswer(
      (_) async => const NotificationSettingsModel(
        pomodoroEnabled: true,
        longBreakEnabled: true,
        dailyReminderEnabled: true,
        dailyGoalEnabled: true,
        streakReminderEnabled: true,
        widgetAutoUpdateEnabled: true,
        quietHoursEnabled: false,
        hasFcmToken: true,
      ),
    );
    final entity = await repo.updateFcmToken('local-stub-1234567890');
    expect(entity.hasFcmToken, isTrue);
  });
}
