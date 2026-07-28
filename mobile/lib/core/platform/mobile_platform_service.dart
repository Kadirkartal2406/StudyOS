import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';

import 'platform_service.dart';

class MobilePlatformService implements PlatformService {
  @override
  Future<bool> areNotificationsAllowed() async {
    if (kIsWeb) return false;
    final status = await Permission.notification.status;
    return status.isGranted;
  }

  @override
  Future<bool> requestNotificationPermission() async {
    if (kIsWeb) return false;
    final status = await Permission.notification.request();
    return status.isGranted;
  }

  @override
  Future<bool> canScheduleExactAlarms() async {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) {
      return true;
    }
    final status = await Permission.scheduleExactAlarm.status;
    return status.isGranted || status.isLimited;
  }

  @override
  Future<void> openSystemNotificationSettings() async {
    await openAppSettings();
  }
}
