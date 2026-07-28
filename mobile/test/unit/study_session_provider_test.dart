import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/study_session/domain/entities/pomodoro_preset.dart';
import 'package:studyos_mobile/features/study_session/domain/entities/study_session_entity.dart';
import 'package:studyos_mobile/features/study_session/domain/entities/study_session_status.dart';
import 'package:studyos_mobile/features/study_session/domain/repositories/study_session_repository.dart';
import 'package:studyos_mobile/features/study_session/presentation/providers/study_session_provider.dart';
import 'package:studyos_mobile/features/study_session/presentation/providers/study_session_state.dart';
import 'package:studyos_mobile/services/pomodoro_notification_service.dart';

class _FakeRepo implements StudySessionRepository {
  StudySessionEntity? active;
  int startCalls = 0;

  StudySessionEntity _session({
    StudySessionStatus status = StudySessionStatus.running,
  }) {
    final now = DateTime.now().toUtc();
    return StudySessionEntity(
      id: 'sess-1',
      userId: 'user-1',
      startedAt: now,
      plannedDurationMinutes: 25,
      actualDurationMinutes: 0,
      breakDurationMinutes: 5,
      completedQuestions: 0,
      completedTopics: 0,
      status: status,
      createdAt: now,
      updatedAt: now,
    );
  }

  @override
  Future<StudySessionEntity> start({
    required int plannedDurationMinutes,
    required int breakDurationMinutes,
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
  }) async {
    startCalls++;
    active = _session();
    return active!;
  }

  @override
  Future<StudySessionEntity> pause() async {
    active = _session(status: StudySessionStatus.paused);
    return active!;
  }

  @override
  Future<StudySessionEntity> resume() async {
    active = _session();
    return active!;
  }

  @override
  Future<StudySessionEntity> finish({
    int? completedQuestions,
    int? completedTopics,
  }) async {
    active = _session(status: StudySessionStatus.completed);
    return active!;
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
  Future<StudySessionEntity> getById(String id) async => _session();
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
  late _FakeRepo repo;
  late ProviderContainer container;

  setUp(() {
    repo = _FakeRepo();
    container = ProviderContainer(
      overrides: [
        studySessionRepositoryProvider.overrideWithValue(repo),
        pomodoroNotificationServiceProvider.overrideWithValue(
          _FakeNotifications(),
        ),
      ],
    );
  });

  tearDown(() => container.dispose());

  StudySessionNotifier notifier() =>
      container.read(studySessionProvider.notifier);

  StudySessionReady ready() =>
      container.read(studySessionProvider) as StudySessionReady;

  test('initial state is idle with default preset', () {
    expect(ready().phase, PomodoroPhase.idle);
    expect(ready().focusMinutes, 25);
    expect(ready().breakMinutes, 5);
    expect(ready().remainingSeconds, 25 * 60);
  });

  test('selectPreset updates durations when idle', () {
    notifier().selectPreset(PomodoroPreset.defaults[1]);
    expect(ready().focusMinutes, 50);
    expect(ready().breakMinutes, 10);
    expect(ready().remainingSeconds, 50 * 60);
  });

  test('start creates session and enters focus', () async {
    await notifier().start();
    expect(repo.startCalls, 1);
    expect(ready().phase, PomodoroPhase.focus);
    expect(ready().isRunning, isTrue);
    expect(ready().session, isNotNull);
  });

  test('pause and resume cycle', () async {
    await notifier().start();
    await notifier().pause();
    expect(ready().isRunning, isFalse);
    expect(ready().session?.status, StudySessionStatus.paused);

    await notifier().resume();
    expect(ready().isRunning, isTrue);
    expect(ready().session?.status, StudySessionStatus.running);
  });

  test('finish returns to idle', () async {
    await notifier().start();
    await notifier().finish(completedQuestions: 5);
    expect(ready().phase, PomodoroPhase.idle);
    expect(ready().session, isNull);
    expect(ready().isRunning, isFalse);
  });

  test('setCustomDuration validates range', () {
    notifier().setCustomDuration(focusMinutes: 40, breakMinutes: 8);
    expect(ready().focusMinutes, 40);
    expect(ready().breakMinutes, 8);

    notifier().setCustomDuration(focusMinutes: 0, breakMinutes: 5);
    expect(ready().focusMinutes, 40);
  });
}
