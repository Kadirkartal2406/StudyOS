import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import '../../../../core/platform/local_notification_service.dart';
import '../../domain/entities/study_session_entity.dart';

/// M25 — kilit ekranı / ongoing Study Session bildirimi.
///
/// Android: ongoing notification + aksiyon butonları (Molaya Çık / Derse Dön).
/// Foreground Service / home widget / iOS Live Activities: mimari hazır (P1).
typedef StudySessionNotificationActionHandler = Future<void> Function(
  StudySessionLiveAction action,
);

enum StudySessionLiveAction {
  takeBreak,
  resumeStudy,
  openSession,
}

class StudySessionLiveNotificationService {
  StudySessionLiveNotificationService({
    required LocalNotificationService notifications,
  }) : _notifications = notifications;

  static const int notificationId = 2501;
  static const String channelId = 'study_session_live';
  static const String actionBreak = 'study_session_break';
  static const String actionResume = 'study_session_resume';
  static const String actionOpen = 'study_session_open';

  final LocalNotificationService _notifications;
  StudySessionNotificationActionHandler? _onAction;
  bool _wired = false;

  void setActionHandler(StudySessionNotificationActionHandler? handler) {
    _onAction = handler;
  }

  Future<void> init() async {
    if (!_wired) {
      _notifications.setOnNotificationResponse(_handleResponse);
      _wired = true;
    }
    await _notifications.init();
  }

  Future<void> showStudying({
    required String subject,
    required String topic,
    required String elapsedHms,
    String? todayTotalLabel,
  }) async {
    if (kIsWeb) return;
    await init();
    final bodyParts = <String>[
      if (topic.trim().isNotEmpty) topic.trim(),
      elapsedHms,
      if (todayTotalLabel != null && todayTotalLabel.isNotEmpty)
        'Bugün $todayTotalLabel',
    ];
    await _notifications.showOngoing(
      id: notificationId,
      title: '📚 $subject',
      body: bodyParts.join(' · '),
      channelId: channelId,
      channelName: 'Çalışma oturumu',
      payload: actionOpen,
      actions: const [
        AndroidNotificationAction(
          actionBreak,
          '☕ Molaya Çık',
          showsUserInterface: false,
          cancelNotification: false,
        ),
      ],
      colorHex: 0xFF1B7A5A,
    );
  }

  Future<void> showBreak({
    required String elapsedHms,
    String? nextSubject,
  }) async {
    if (kIsWeb) return;
    await init();
    final body = nextSubject != null && nextSubject.isNotEmpty
        ? '$elapsedHms · Sonraki: $nextSubject'
        : elapsedHms;
    await _notifications.showOngoing(
      id: notificationId,
      title: '☕ Mola',
      body: body,
      channelId: channelId,
      channelName: 'Çalışma oturumu',
      payload: actionOpen,
      actions: const [
        AndroidNotificationAction(
          actionResume,
          '📚 Derse Dön',
          showsUserInterface: false,
          cancelNotification: false,
        ),
      ],
      colorHex: 0xFFE67E22,
    );
  }

  Future<void> clear() async {
    if (kIsWeb) return;
    await _notifications.cancel(notificationId);
  }

  Future<void> syncFromEngine({
    required StudyEngineState engineState,
    required String subject,
    required String topic,
    required String elapsedHms,
    String? todayTotalLabel,
    String? nextSubject,
  }) async {
    switch (engineState) {
      case StudyEngineState.studying:
        await showStudying(
          subject: subject,
          topic: topic,
          elapsedHms: elapsedHms,
          todayTotalLabel: todayTotalLabel,
        );
      case StudyEngineState.breakTime:
        await showBreak(
          elapsedHms: elapsedHms,
          nextSubject: nextSubject ?? subject,
        );
      case StudyEngineState.paused:
      case StudyEngineState.idle:
      case StudyEngineState.completed:
        await clear();
    }
  }

  void _handleResponse(NotificationResponse response) {
    final actionId = response.actionId;
    final payload = response.payload;
    final StudySessionLiveAction? mapped = switch (actionId) {
      actionBreak => StudySessionLiveAction.takeBreak,
      actionResume => StudySessionLiveAction.resumeStudy,
      _ => (payload == actionOpen || actionId == null || actionId.isEmpty)
          ? StudySessionLiveAction.openSession
          : null,
    };
    if (mapped == null) return;
    final handler = _onAction;
    if (handler != null) {
      handler(mapped);
    }
  }
}
