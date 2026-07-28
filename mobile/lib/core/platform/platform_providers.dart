import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'home_widget_service.dart';
import 'local_notification_service.dart';
import 'mobile_platform_service.dart';
import 'notification_service.dart';
import 'platform_service.dart';
import 'quick_actions_shortcut_service.dart';
import 'shortcut_service.dart';
import 'widget_service.dart';

final platformServiceProvider = Provider<PlatformService>((ref) {
  return MobilePlatformService();
});

final appNotificationServiceProvider = Provider<NotificationService>((ref) {
  return LocalNotificationService();
});

final widgetServiceProvider = Provider<WidgetService>((ref) {
  if (kIsWeb) return NoOpWidgetService();
  return HomeWidgetService();
});

final liveActivityServiceProvider = Provider<LiveActivityService>((ref) {
  return StubLiveActivityService();
});

final shortcutServiceProvider = Provider<ShortcutService>((ref) {
  if (kIsWeb) return NoOpShortcutService();
  return QuickActionsShortcutService();
});
