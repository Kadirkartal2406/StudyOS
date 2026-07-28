import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/analytics/analytics_service.dart';
import 'core/platform/platform_providers.dart';
import 'core/platform/shortcut_service.dart';
import 'core/router/app_router.dart';
import 'core/session/session_scope.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/presentation/providers/auth_provider.dart';
import 'features/auth/presentation/providers/auth_state.dart';
import 'features/notification_settings/presentation/providers/notification_settings_provider.dart';
import 'features/study_session/presentation/providers/study_session_provider.dart';
import 'features/theme/presentation/providers/theme_preferences_provider.dart';

/// StudyOS mobil uygulamasının kök widget'ı.
class StudyOSApp extends ConsumerStatefulWidget {
  const StudyOSApp({super.key});

  @override
  ConsumerState<StudyOSApp> createState() => _StudyOSAppState();
}

class _StudyOSAppState extends ConsumerState<StudyOSApp> {
  var _bootstrapped = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    if (_bootstrapped) return;
    _bootstrapped = true;

    try {
      await ref.read(appNotificationServiceProvider).init();
    } catch (_) {
      // Test / desteklenmeyen platform.
    }

    try {
      await ref.read(studySessionLiveNotificationProvider).init();
    } catch (_) {}

    final auth = ref.read(authProvider);
    if (auth is AuthAuthenticated) {
      unawaited(
        ref.read(studySessionProvider.notifier).restoreActiveSession(),
      );
    }

    try {
      await ref.read(shortcutServiceProvider).registerDefaults(
        onAction: (action) {
          final router = ref.read(appRouterProvider);
          switch (action) {
            case AppShortcutAction.startPomodoro:
            case AppShortcutAction.pausePomodoro:
            case AppShortcutAction.resumePomodoro:
              router.go('/pomodoro');
            case AppShortcutAction.openTodayPlan:
              router.go('/study-plan');
            case AppShortcutAction.openDashboard:
              router.go('/dashboard');
          }
        },
      );
    } catch (_) {
      // Quick Actions test ortamında olmayabilir.
    }

    try {
      ref.read(analyticsServiceProvider).trackSync(AnalyticsEvents.appOpen);
    } catch (_) {}
  }

  Future<void> _syncFcmStubIfNeeded() async {
    try {
      final token = await ref.read(appNotificationServiceProvider).getFcmToken();
      if (token == null) return;
      final settings = ref.read(notificationSettingsProvider);
      if (settings is NotificationSettingsLoaded &&
          settings.settings.hasFcmToken) {
        return;
      }
      await ref
          .read(notificationSettingsRepositoryProvider)
          .updateFcmToken(token);
    } catch (_) {
      // Stub senkronu UI'yi bozmamalı.
    }
  }

  @override
  Widget build(BuildContext context) {
    // Hesap değişince kullanıcıya özel Riverpod cache temizliği
    ref.watch(sessionScopeProvider);
    final router = ref.watch(appRouterProvider);
    final themePrefs = ref.watch(themePreferencesProvider);

    ref.listen<AuthState>(authProvider, (prev, next) {
      if (next is AuthAuthenticated && prev is! AuthAuthenticated) {
        unawaited(_syncFcmStubIfNeeded());
        unawaited(
          ref.read(studySessionProvider.notifier).restoreActiveSession(),
        );
      }
    });

    return MaterialApp.router(
      title: 'StudyOS',
      theme: AppTheme.lightTheme(seed: themePrefs.accent),
      darkTheme: AppTheme.darkTheme(seed: themePrefs.accent),
      themeMode: themePrefs.mode,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
