/// Ana ekran / Live Activity / Wear widget ortak sözleşmesi (G).
/// Sprint-1.8: Android Medium home widget; iOS Live Activities stub.
class WidgetSnapshot {
  const WidgetSnapshot({
    required this.todayStudyMinutes,
    required this.dailyGoalMinutes,
    required this.progressPercentage,
    this.activePlanTitle,
    this.pomodoroRemainingLabel,
    this.isPomodoroActive = false,
    this.goalLabel,
  });

  final int todayStudyMinutes;
  final int dailyGoalMinutes;
  final double progressPercentage;
  final String? activePlanTitle;
  final String? pomodoroRemainingLabel;
  final bool isPomodoroActive;
  /// Aktif hedef satırı, örn. "Hedef: 42%".
  final String? goalLabel;
}

abstract class WidgetService {
  /// Cache'ten widget verisini yazar ve yeniler (F — backend bağımsız).
  Future<void> updateFromCache(WidgetSnapshot snapshot);

  /// Yalnızca pomodoro satırını günceller; günlük metrikleri korur.
  Future<void> updatePomodoroOverlay({
    required bool isActive,
    String? remainingLabel,
    String? planTitle,
  });

  Future<void> requestRefresh();
}

/// iOS Live Activities / Dynamic Island için ileride ActivityKit bağlanacak stub.
abstract class LiveActivityService {
  Future<void> startPomodoroActivity({
    required String title,
    required Duration remaining,
  });

  Future<void> updatePomodoroActivity({required Duration remaining});

  Future<void> endPomodoroActivity();
}

class StubLiveActivityService implements LiveActivityService {
  @override
  Future<void> startPomodoroActivity({
    required String title,
    required Duration remaining,
  }) async {}

  @override
  Future<void> updatePomodoroActivity({required Duration remaining}) async {}

  @override
  Future<void> endPomodoroActivity() async {}
}

/// Test / web — widget güncellemesi yok.
class NoOpWidgetService implements WidgetService {
  @override
  Future<void> updateFromCache(WidgetSnapshot snapshot) async {}

  @override
  Future<void> updatePomodoroOverlay({
    required bool isActive,
    String? remainingLabel,
    String? planTitle,
  }) async {}

  @override
  Future<void> requestRefresh() async {}
}
