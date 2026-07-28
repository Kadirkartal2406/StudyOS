import 'package:flutter/foundation.dart';
import 'package:flutter/painting.dart' show Color;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;

import 'notification_service.dart';

/// Local notification implementasyonu (A1). FCM token stub.
class LocalNotificationService implements NotificationService {
  LocalNotificationService();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  bool _initialized = false;
  String? _stubFcmToken;
  void Function(NotificationResponse response)? _onResponse;

  /// M25 — kilit ekranı aksiyonları için callback.
  void setOnNotificationResponse(
    void Function(NotificationResponse response)? handler,
  ) {
    _onResponse = handler;
  }

  @override
  Future<void> init() async {
    if (_initialized) return;
    try {
      tz_data.initializeTimeZones();

      const android = AndroidInitializationSettings('@mipmap/ic_launcher');
      const ios = DarwinInitializationSettings(
        requestAlertPermission: true,
        requestBadgePermission: true,
        requestSoundPermission: true,
      );
      await _plugin.initialize(
        const InitializationSettings(android: android, iOS: ios),
        onDidReceiveNotificationResponse: (response) {
          _onResponse?.call(response);
        },
      );
      await _plugin
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.requestNotificationsPermission();
    } catch (_) {
      // Test / unsupported platform — stub token yine de üretilebilir.
    }

    // FCM altyapı stub — gerçek FirebaseMessaging sonraki sprint.
    _stubFcmToken = kIsWeb
        ? null
        : 'local-stub-${DateTime.now().millisecondsSinceEpoch}';
    _initialized = true;
  }

  @override
  Future<void> show({
    required AppNotificationType type,
    required String title,
    required String body,
  }) async {
    await init();
    await _plugin.show(
      DateTime.now().millisecondsSinceEpoch.remainder(100000),
      title,
      body,
      _detailsFor(type),
    );
  }

  /// Ongoing / kilit ekranı Study Session kartı (M25).
  Future<void> showOngoing({
    required int id,
    required String title,
    required String body,
    required String channelId,
    required String channelName,
    String? payload,
    List<AndroidNotificationAction> actions = const [],
    int? colorHex,
  }) async {
    if (kIsWeb) return;
    await init();
    final androidPlugin = _plugin.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    await androidPlugin?.createNotificationChannel(
      AndroidNotificationChannel(
        channelId,
        channelName,
        description: 'Aktif çalışma ve mola sayacı',
        importance: Importance.low,
        playSound: false,
        enableVibration: false,
      ),
    );
    await _plugin.show(
      id,
      title,
      body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          channelId,
          channelName,
          channelDescription: 'Aktif çalışma ve mola sayacı',
          importance: Importance.low,
          priority: Priority.low,
          ongoing: true,
          autoCancel: false,
          onlyAlertOnce: true,
          showWhen: false,
          category: AndroidNotificationCategory.progress,
          color: colorHex != null ? Color(colorHex) : null,
          actions: actions,
          playSound: false,
          enableVibration: false,
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentSound: false,
        ),
      ),
      payload: payload,
    );
  }

  @override
  Future<void> schedule({
    required AppNotificationType type,
    required String title,
    required String body,
    required Duration after,
    required int notificationId,
  }) async {
    await init();
    await _plugin.cancel(notificationId);
    await _plugin.zonedSchedule(
      notificationId,
      title,
      body,
      tz.TZDateTime.now(tz.local).add(after),
      _detailsFor(type),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
    );
  }

  @override
  Future<void> cancel(int notificationId) => _plugin.cancel(notificationId);

  @override
  Future<void> cancelAll() => _plugin.cancelAll();

  @override
  Future<String?> getFcmToken() async {
    await init();
    return _stubFcmToken;
  }

  NotificationDetails _detailsFor(AppNotificationType type) {
    final channelId = switch (type) {
      AppNotificationType.pomodoroStarted ||
      AppNotificationType.pomodoroCompleted ||
      AppNotificationType.longBreak =>
        'pomodoro_channel',
      AppNotificationType.dailyGoalCompleted ||
      AppNotificationType.studyReminder ||
      AppNotificationType.streakWarning ||
      AppNotificationType.goalMilestone ||
      AppNotificationType.examMilestone ||
      AppNotificationType.plannerReady ||
      AppNotificationType.revisionDue ||
      AppNotificationType.achievementUnlocked =>
        'reminder_channel',
      AppNotificationType.widgetUpdated => 'widget_channel',
    };
    final channelName = switch (type) {
      AppNotificationType.pomodoroStarted ||
      AppNotificationType.pomodoroCompleted ||
      AppNotificationType.longBreak =>
        'Pomodoro',
      AppNotificationType.dailyGoalCompleted ||
      AppNotificationType.studyReminder ||
      AppNotificationType.streakWarning ||
      AppNotificationType.goalMilestone ||
      AppNotificationType.examMilestone ||
      AppNotificationType.plannerReady ||
      AppNotificationType.revisionDue ||
      AppNotificationType.achievementUnlocked =>
        'Hatırlatıcılar',
      AppNotificationType.widgetUpdated => 'Widget',
    };
    return NotificationDetails(
      android: AndroidNotificationDetails(
        channelId,
        channelName,
        channelDescription: 'StudyOS bildirimleri',
        importance: Importance.high,
        priority: Priority.high,
        playSound: true,
        enableVibration: true,
      ),
      iOS: const DarwinNotificationDetails(
        presentAlert: true,
        presentSound: true,
      ),
    );
  }
}
