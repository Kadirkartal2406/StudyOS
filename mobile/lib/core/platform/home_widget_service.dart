import 'package:flutter/foundation.dart';
import 'package:home_widget/home_widget.dart';

import 'widget_service.dart';

/// Android home widget — cache SharedPreferences + home_widget (F).
class HomeWidgetService implements WidgetService {
  static const androidName = 'StudyOsMediumWidgetProvider';

  @override
  Future<void> updateFromCache(WidgetSnapshot snapshot) async {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) return;

    await HomeWidget.saveWidgetData<int>(
      'today_study_minutes',
      snapshot.todayStudyMinutes,
    );
    await HomeWidget.saveWidgetData<int>(
      'daily_goal_minutes',
      snapshot.dailyGoalMinutes,
    );
    await HomeWidget.saveWidgetData<String>(
      'progress_label',
      '${snapshot.progressPercentage.toStringAsFixed(0)}%',
    );
    await HomeWidget.saveWidgetData<String>(
      'plan_title',
      snapshot.activePlanTitle ?? 'Plan yok',
    );
    await HomeWidget.saveWidgetData<String>(
      'pomodoro_label',
      snapshot.isPomodoroActive
          ? (snapshot.pomodoroRemainingLabel ?? 'Aktif')
          : 'Pomodoro yok',
    );
    await HomeWidget.saveWidgetData<String>(
      'goal_label',
      snapshot.goalLabel ?? 'Hedef yok',
    );
    await HomeWidget.updateWidget(
      name: androidName,
      androidName: androidName,
    );
  }

  @override
  Future<void> updatePomodoroOverlay({
    required bool isActive,
    String? remainingLabel,
    String? planTitle,
  }) async {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) return;

    if (planTitle != null) {
      await HomeWidget.saveWidgetData<String>('plan_title', planTitle);
    }
    await HomeWidget.saveWidgetData<String>(
      'pomodoro_label',
      isActive ? (remainingLabel ?? 'Aktif') : 'Pomodoro yok',
    );
    await HomeWidget.updateWidget(
      name: androidName,
      androidName: androidName,
    );
  }

  @override
  Future<void> requestRefresh() async {
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) return;
    await HomeWidget.updateWidget(
      name: androidName,
      androidName: androidName,
    );
  }
}
