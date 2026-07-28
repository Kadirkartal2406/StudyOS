import 'package:flutter/foundation.dart';
import 'package:quick_actions/quick_actions.dart';

import 'shortcut_service.dart';

class QuickActionsShortcutService implements ShortcutService {
  final QuickActions _quickActions = const QuickActions();

  @override
  Future<void> registerDefaults({
    required void Function(AppShortcutAction action) onAction,
  }) async {
    if (kIsWeb) return;

    await _quickActions.initialize((type) {
      final action = switch (type) {
        'start_pomodoro' => AppShortcutAction.startPomodoro,
        'pause_pomodoro' => AppShortcutAction.pausePomodoro,
        'resume_pomodoro' => AppShortcutAction.resumePomodoro,
        'open_today_plan' => AppShortcutAction.openTodayPlan,
        'open_dashboard' => AppShortcutAction.openDashboard,
        _ => null,
      };
      if (action != null) onAction(action);
    });

    await _quickActions.setShortcutItems(const [
      ShortcutItem(
        type: 'start_pomodoro',
        localizedTitle: 'Pomodoro Başlat',
        icon: 'ic_launcher',
      ),
      ShortcutItem(
        type: 'pause_pomodoro',
        localizedTitle: 'Pomodoro Durdur',
        icon: 'ic_launcher',
      ),
      ShortcutItem(
        type: 'resume_pomodoro',
        localizedTitle: 'Pomodoro Devam Et',
        icon: 'ic_launcher',
      ),
      ShortcutItem(
        type: 'open_today_plan',
        localizedTitle: 'Bugünkü Plan',
        icon: 'ic_launcher',
      ),
      ShortcutItem(
        type: 'open_dashboard',
        localizedTitle: 'Dashboard',
        icon: 'ic_launcher',
      ),
    ]);
  }
}

class NoOpShortcutService implements ShortcutService {
  @override
  Future<void> registerDefaults({
    required void Function(AppShortcutAction action) onAction,
  }) async {}
}
