import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/study_session/domain/entities/study_session_entity.dart';
import 'package:studyos_mobile/features/study_session/domain/entities/study_session_status.dart';
import 'package:studyos_mobile/features/study_session/domain/repositories/study_session_repository.dart';
import 'package:studyos_mobile/features/study_session/presentation/providers/study_session_provider.dart';
import 'package:studyos_mobile/features/study_session/presentation/screens/pomodoro_screen.dart';
import 'package:studyos_mobile/services/pomodoro_notification_service.dart';

class _FakeRepo implements StudySessionRepository {
  @override
  Future<StudySessionEntity> start({
    required int plannedDurationMinutes,
    required int breakDurationMinutes,
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
  }) async {
    final now = DateTime.now().toUtc();
    return StudySessionEntity(
      id: 'sess-1',
      userId: 'user-1',
      startedAt: now,
      plannedDurationMinutes: plannedDurationMinutes,
      actualDurationMinutes: 0,
      breakDurationMinutes: breakDurationMinutes,
      completedQuestions: 0,
      completedTopics: 0,
      status: StudySessionStatus.running,
      createdAt: now,
      updatedAt: now,
    );
  }

  @override
  Future<StudySessionEntity> pause() async => start(
        plannedDurationMinutes: 25,
        breakDurationMinutes: 5,
      );

  @override
  Future<StudySessionEntity> resume() async => start(
        plannedDurationMinutes: 25,
        breakDurationMinutes: 5,
      );

  @override
  Future<StudySessionEntity> finish({
    int? completedQuestions,
    int? completedTopics,
  }) async {
    final now = DateTime.now().toUtc();
    return StudySessionEntity(
      id: 'sess-1',
      userId: 'user-1',
      startedAt: now,
      endedAt: now,
      plannedDurationMinutes: 25,
      actualDurationMinutes: 1,
      breakDurationMinutes: 5,
      completedQuestions: completedQuestions ?? 0,
      completedTopics: completedTopics ?? 0,
      status: StudySessionStatus.completed,
      createdAt: now,
      updatedAt: now,
    );
  }

  @override
  Future<List<StudySessionEntity>> getToday() async => [];

  @override
  Future<StudySessionHistoryResult> getHistory({
    int page = 1,
    int pageSize = 20,
    DateTime? dateFrom,
    DateTime? dateTo,
    String? studyPlanId,
    String? status,
    String? q,
  }) async =>
      const StudySessionHistoryResult(
        items: [],
        page: 1,
        pageSize: 20,
        totalItems: 0,
        totalPages: 0,
      );

  @override
  Future<StudySessionEntity> getById(String id) async => start(
        plannedDurationMinutes: 25,
        breakDurationMinutes: 5,
      );
}

class _FakeNotifications extends PomodoroNotificationService {
  @override
  Future<void> init() async {}

  @override
  Future<void> scheduleFocusEnd({required Duration after}) async {}

  @override
  Future<void> scheduleBreakEnd({required Duration after}) async {}

  @override
  Future<void> showImmediate({
    required String title,
    required String body,
  }) async {}

  @override
  Future<void> cancelAll() async {}
}

void main() {
  testWidgets('shows countdown and start button', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          studySessionRepositoryProvider.overrideWithValue(_FakeRepo()),
          pomodoroNotificationServiceProvider.overrideWithValue(
            _FakeNotifications(),
          ),
        ],
        child: const MaterialApp(home: PomodoroScreen()),
      ),
    );

    expect(find.text('Başlat'), findsOneWidget);
    expect(find.text('25:00'), findsOneWidget);
    expect(find.text('25 / 5'), findsOneWidget);
  });

  testWidgets('start then shows pause and finish', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          studySessionRepositoryProvider.overrideWithValue(_FakeRepo()),
          pomodoroNotificationServiceProvider.overrideWithValue(
            _FakeNotifications(),
          ),
        ],
        child: const MaterialApp(home: PomodoroScreen()),
      ),
    );

    await tester.tap(find.text('Başlat'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Duraklat'), findsOneWidget);
    expect(find.text('Bitir'), findsOneWidget);
  });
}
