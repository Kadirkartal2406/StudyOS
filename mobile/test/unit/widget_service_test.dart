import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/core/platform/widget_service.dart';

class _RecordingWidgetService implements WidgetService {
  WidgetSnapshot? lastSnapshot;
  bool? lastPomodoroActive;
  String? lastPomodoroLabel;

  @override
  Future<void> updateFromCache(WidgetSnapshot snapshot) async {
    lastSnapshot = snapshot;
  }

  @override
  Future<void> updatePomodoroOverlay({
    required bool isActive,
    String? remainingLabel,
    String? planTitle,
  }) async {
    lastPomodoroActive = isActive;
    lastPomodoroLabel = remainingLabel;
  }

  @override
  Future<void> requestRefresh() async {}
}

void main() {
  test('WidgetSnapshot alanları taşır', () {
    const snap = WidgetSnapshot(
      todayStudyMinutes: 45,
      dailyGoalMinutes: 120,
      progressPercentage: 37.5,
      activePlanTitle: 'Matematik',
      isPomodoroActive: true,
      pomodoroRemainingLabel: '24:00',
    );
    expect(snap.todayStudyMinutes, 45);
    expect(snap.isPomodoroActive, isTrue);
  });

  test('NoOpWidgetService sessizce tamamlanır', () async {
    const snap = WidgetSnapshot(
      todayStudyMinutes: 10,
      dailyGoalMinutes: 60,
      progressPercentage: 16.6,
    );
    await NoOpWidgetService().updateFromCache(snap);
    await NoOpWidgetService().updatePomodoroOverlay(isActive: false);
    await NoOpWidgetService().requestRefresh();
  });

  test('Recording service cache güncellemesini saklar', () async {
    final service = _RecordingWidgetService();
    await service.updateFromCache(
      const WidgetSnapshot(
        todayStudyMinutes: 20,
        dailyGoalMinutes: 100,
        progressPercentage: 20,
      ),
    );
    expect(service.lastSnapshot?.todayStudyMinutes, 20);

    await service.updatePomodoroOverlay(
      isActive: true,
      remainingLabel: '12:30',
    );
    expect(service.lastPomodoroActive, isTrue);
    expect(service.lastPomodoroLabel, '12:30');
  });
}
