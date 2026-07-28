/// OS App Shortcuts / App Intents ortak sözleşmesi.
enum AppShortcutAction {
  startPomodoro,
  pausePomodoro,
  resumePomodoro,
  openTodayPlan,
  openDashboard,
}

abstract class ShortcutService {
  Future<void> registerDefaults({
    required void Function(AppShortcutAction action) onAction,
  });
}
