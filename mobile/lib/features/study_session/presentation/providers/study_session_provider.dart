import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/local_notification_service.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../../../core/platform/widget_service.dart';
import '../../../../services/pomodoro_notification_service.dart';
import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../notification_settings/presentation/providers/notification_settings_provider.dart';
import '../../../statistics/presentation/providers/statistics_provider.dart';
import '../../../study_plan/presentation/providers/study_plan_provider.dart';
import '../../data/datasources/study_session_remote_datasource.dart';
import '../../data/repositories/study_session_repository_impl.dart';
import '../../domain/entities/pomodoro_preset.dart';
import '../../domain/entities/study_session_entity.dart';
import '../../domain/entities/study_session_status.dart';
import '../../domain/repositories/study_session_repository.dart';
import '../../domain/usecases/finish_study_session_usecase.dart';
import '../../domain/usecases/pause_study_session_usecase.dart';
import '../../domain/usecases/resume_study_session_usecase.dart';
import '../../domain/usecases/start_study_session_usecase.dart';
import '../services/study_session_live_notification_service.dart';
import '../widgets/today_summary_card.dart';
import 'study_session_state.dart';

// ── Dependency Injection ────────────────────────────────────────────────────

final pomodoroNotificationServiceProvider =
    Provider<PomodoroNotificationService>((ref) {
  final notifications = ref.watch(appNotificationServiceProvider);
  return PomodoroNotificationService(
    notificationService: notifications is LocalNotificationService
        ? notifications
        : null,
  );
});

final studySessionLiveNotificationProvider =
    Provider<StudySessionLiveNotificationService>((ref) {
  final notifications = ref.watch(appNotificationServiceProvider);
  if (notifications is! LocalNotificationService) {
    return StudySessionLiveNotificationService(
      notifications: LocalNotificationService(),
    );
  }
  return StudySessionLiveNotificationService(notifications: notifications);
});

final _remoteDatasourceProvider = Provider<StudySessionRemoteDatasource>((ref) {
  return StudySessionRemoteDatasource(ref.watch(dioClientProvider));
});

final studySessionRepositoryProvider = Provider<StudySessionRepository>((ref) {
  return StudySessionRepositoryImpl(ref.watch(_remoteDatasourceProvider));
});

final _startUsecaseProvider = Provider<StartStudySessionUsecase>((ref) {
  return StartStudySessionUsecase(ref.watch(studySessionRepositoryProvider));
});

final _pauseUsecaseProvider = Provider<PauseStudySessionUsecase>((ref) {
  return PauseStudySessionUsecase(ref.watch(studySessionRepositoryProvider));
});

final _resumeUsecaseProvider = Provider<ResumeStudySessionUsecase>((ref) {
  return ResumeStudySessionUsecase(ref.watch(studySessionRepositoryProvider));
});

final _finishUsecaseProvider = Provider<FinishStudySessionUsecase>((ref) {
  return FinishStudySessionUsecase(ref.watch(studySessionRepositoryProvider));
});

// ── Notifier ────────────────────────────────────────────────────────────────

class StudySessionNotifier extends StateNotifier<StudySessionState> {
  StudySessionNotifier({
    required StartStudySessionUsecase start,
    required PauseStudySessionUsecase pause,
    required ResumeStudySessionUsecase resume,
    required FinishStudySessionUsecase finish,
    required StudySessionRepository repository,
    required PomodoroNotificationService notifications,
    StudySessionLiveNotificationService? liveNotification,
    WidgetService? widgetService,
    bool Function()? pomodoroNotificationsEnabled,
    bool Function()? longBreakNotificationsEnabled,
    this.onSessionCompleted,
  })  : _start = start,
        _pause = pause,
        _resume = resume,
        _finish = finish,
        _repository = repository,
        _notifications = notifications,
        _liveNotification = liveNotification,
        _widgetService = widgetService,
        _pomodoroNotificationsEnabled =
            pomodoroNotificationsEnabled ?? (() => true),
        _longBreakNotificationsEnabled =
            longBreakNotificationsEnabled ?? (() => true),
        super(StudySessionReady.idle());

  final StartStudySessionUsecase _start;
  final PauseStudySessionUsecase _pause;
  final ResumeStudySessionUsecase _resume;
  final FinishStudySessionUsecase _finish;
  final StudySessionRepository _repository;
  final PomodoroNotificationService _notifications;
  final StudySessionLiveNotificationService? _liveNotification;
  final WidgetService? _widgetService;
  final bool Function() _pomodoroNotificationsEnabled;
  final bool Function() _longBreakNotificationsEnabled;
  final void Function()? onSessionCompleted;

  Timer? _ticker;
  int _liveSyncTick = 0;

  StudySessionReady get _ready => state as StudySessionReady;

  void selectPreset(PomodoroPreset preset) {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.phase != PomodoroPhase.idle || current.isMutating) return;
    state = StudySessionReady.idle(preset: preset).copyWith(
      subject: current.subject,
      topic: current.topic,
      studyPlanId: current.studyPlanId,
    );
  }

  void setCustomDuration({
    required int focusMinutes,
    required int breakMinutes,
  }) {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.phase != PomodoroPhase.idle || current.isMutating) return;
    if (focusMinutes < 1 || focusMinutes > 240) return;
    if (breakMinutes < 0 || breakMinutes > 60) return;
    state = current.copyWith(
      focusMinutes: focusMinutes,
      breakMinutes: breakMinutes,
      remainingSeconds: focusMinutes * 60,
      elapsedSeconds: 0,
      phase: PomodoroPhase.idle,
      isRunning: false,
      clearError: true,
    );
  }

  void setContext({
    String? subject,
    String? topic,
    String? subjectCode,
    String? topicCode,
    String? studyPlanId,
  }) {
    if (state is! StudySessionReady) return;
    state = _ready.copyWith(
      subject: subject,
      topic: topic,
      subjectCode: subjectCode,
      topicCode: topicCode,
      studyPlanId: studyPlanId,
    );
  }

  void setChronometerMode(bool enabled) {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.phase != PomodoroPhase.idle || current.isMutating) return;
    state = StudySessionReady.idle(
      preset: PomodoroPreset(
        focusMinutes: current.focusMinutes,
        breakMinutes: current.breakMinutes,
        label: enabled ? 'Kronometre' : '${current.focusMinutes} / ${current.breakMinutes}',
      ),
      isChronometer: enabled,
    ).copyWith(
      subject: current.subject,
      topic: current.topic,
      subjectCode: current.subjectCode,
      topicCode: current.topicCode,
      studyPlanId: current.studyPlanId,
    );
  }

  /// M25 — app açılışında DB'deki aktif oturumu geri yükle.
  Future<void> restoreActiveSession() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.session != null && current.phase != PomodoroPhase.idle) return;
    try {
      final session = await _repository.getActive();
      if (session == null) return;
      final now = DateTime.now().toUtc();
      final started = session.startedAt.toUtc();
      var paused = session.pausedSeconds;
      final pausedAt = session.pausedAt?.toUtc();
      if (pausedAt != null) {
        paused += now.difference(pausedAt).inSeconds;
      }
      final openBreak = session.breakStartedAt?.toUtc();
      final openBreakSecs =
          openBreak != null ? now.difference(openBreak).inSeconds : 0;
      final focusElapsed = (now.difference(started).inSeconds -
              paused -
              session.actualBreakMinutes * 60 -
              openBreakSecs)
          .clamp(0, 24 * 3600);

      final isBreak = session.phase == 'break' ||
          session.engineState == StudyEngineState.breakTime;
      final isPaused = session.status == StudySessionStatus.paused;
      final isChronometer = session.mode == 'chronometer';
      final focusMinutes = session.plannedDurationMinutes > 0
          ? session.plannedDurationMinutes
          : current.focusMinutes;
      final breakMinutes = session.breakDurationMinutes > 0
          ? session.breakDurationMinutes
          : (current.breakMinutes > 0 ? current.breakMinutes : 5);

      if (isBreak) {
        state = current.copyWith(
          session: session,
          focusMinutes: focusMinutes,
          breakMinutes: breakMinutes,
          phase: PomodoroPhase.breakTime,
          isRunning: !isPaused,
          isChronometer: isChronometer,
          elapsedSeconds: openBreakSecs.clamp(0, 24 * 3600),
          remainingSeconds: (breakMinutes * 60 - openBreakSecs)
              .clamp(0, breakMinutes * 60),
          savedFocusElapsedSeconds: focusElapsed,
          savedFocusRemainingSeconds: isChronometer
              ? focusElapsed
              : (focusMinutes * 60 - focusElapsed).clamp(0, focusMinutes * 60),
          subject: session.planSubject ?? session.subjectCode ?? current.subject,
          topic: session.planTitle ?? session.topicCode ?? current.topic,
          subjectCode: session.subjectCode ?? current.subjectCode,
          topicCode: session.topicCode ?? current.topicCode,
          studyPlanId: session.studyPlanId ?? current.studyPlanId,
          clearError: true,
          clearBlockedActive: true,
        );
      } else {
        state = current.copyWith(
          session: session,
          focusMinutes: focusMinutes,
          breakMinutes: breakMinutes,
          phase: PomodoroPhase.focus,
          isRunning: !isPaused,
          isChronometer: isChronometer,
          elapsedSeconds: focusElapsed,
          remainingSeconds: isChronometer
              ? focusElapsed
              : (focusMinutes * 60 - focusElapsed).clamp(0, focusMinutes * 60),
          subject: session.planSubject ?? session.subjectCode ?? current.subject,
          topic: session.planTitle ?? session.topicCode ?? current.topic,
          subjectCode: session.subjectCode ?? current.subjectCode,
          topicCode: session.topicCode ?? current.topicCode,
          studyPlanId: session.studyPlanId ?? current.studyPlanId,
          clearError: true,
          clearBlockedActive: true,
        );
      }
      if (!isPaused) {
        _startTicker();
      }
      await _syncLiveNotification(force: true);
    } catch (_) {
      // Restore başarısız olsa UI idle kalır.
    }
  }

  Future<void> handleLiveNotificationAction(
    StudySessionLiveAction action,
  ) async {
    switch (action) {
      case StudySessionLiveAction.takeBreak:
        await takeBreak();
      case StudySessionLiveAction.resumeStudy:
        await endServerBreak();
      case StudySessionLiveAction.openSession:
        break;
    }
  }

  Future<void> start() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.isMutating) return;
    if (current.phase == PomodoroPhase.breakTime) {
      _startBreakTicker(current);
      return;
    }
    if (current.phase != PomodoroPhase.idle && current.session != null) return;

    state = current.copyWith(isMutating: true, clearError: true);
    try {
      final session = await _start(
        plannedDurationMinutes:
            current.isChronometer ? null : current.focusMinutes,
        breakDurationMinutes: current.breakMinutes,
        mode: current.isChronometer ? 'chronometer' : 'pomodoro',
        studyPlanId: current.studyPlanId,
        subjectCode: current.subjectCode,
        topicCode: current.topicCode,
      );
      final remaining =
          current.isChronometer ? 0 : current.focusMinutes * 60;
      state = current.copyWith(
        session: session,
        phase: PomodoroPhase.focus,
        isRunning: true,
        isMutating: false,
        remainingSeconds: remaining,
        elapsedSeconds: 0,
        clearError: true,
      );
      _startTicker();
      if (!current.isChronometer) {
        await _scheduleFocusEnd(Duration(seconds: remaining));
      }
      await _syncPomodoroWidget(
        isActive: true,
        remainingLabel: current.isChronometer
            ? _formatRemaining(0)
            : _formatRemaining(remaining),
        planTitle: current.subject ?? current.topic,
      );
      await _syncLiveNotification(force: true);
    } on AppException catch (e) {
      if (_isActiveSessionConflict(e)) {
        await _presentBlockedActiveSession(
          fallbackMessage: e.message,
          base: current,
        );
        return;
      }
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Oturum başlatılamadı',
      );
    }
  }

  bool _isActiveSessionConflict(AppException e) {
    if (e is ConflictException) {
      final m = e.message.toLowerCase();
      return m.contains('aktif') ||
          m.contains('active session') ||
          m.contains('already exists') ||
          m.contains('oturum var');
    }
    final m = e.message.toLowerCase();
    return m.contains('active session already') ||
        m.contains('zaten aktif bir oturum');
  }

  ({int elapsed, int remaining}) _timingForActiveSession(
    StudySessionEntity session, {
    required int fallbackFocusMinutes,
    required int fallbackBreakMinutes,
  }) {
    final now = DateTime.now().toUtc();
    final started = session.startedAt.toUtc();
    var paused = session.pausedSeconds;
    final pausedAt = session.pausedAt?.toUtc();
    if (pausedAt != null) {
      paused += now.difference(pausedAt).inSeconds;
    }
    final openBreak = session.breakStartedAt?.toUtc();
    final openBreakSecs =
        openBreak != null ? now.difference(openBreak).inSeconds : 0;
    final focusElapsed = (now.difference(started).inSeconds -
            paused -
            session.actualBreakMinutes * 60 -
            openBreakSecs)
        .clamp(0, 24 * 3600);
    final isBreak = session.phase == 'break' ||
        session.engineState == StudyEngineState.breakTime;
    final focusMinutes = session.plannedDurationMinutes > 0
        ? session.plannedDurationMinutes
        : fallbackFocusMinutes;
    final breakMinutes = session.breakDurationMinutes > 0
        ? session.breakDurationMinutes
        : (fallbackBreakMinutes > 0 ? fallbackBreakMinutes : 5);
    final isChronometer = session.mode == 'chronometer';

    if (isBreak) {
      return (
        elapsed: openBreakSecs.clamp(0, 24 * 3600),
        remaining: (breakMinutes * 60 - openBreakSecs).clamp(0, breakMinutes * 60),
      );
    }
    return (
      elapsed: focusElapsed,
      remaining: isChronometer
          ? focusElapsed
          : (focusMinutes * 60 - focusElapsed).clamp(0, focusMinutes * 60),
    );
  }

  Future<void> _presentBlockedActiveSession({
    required String fallbackMessage,
    required StudySessionReady base,
  }) async {
    try {
      final active = await _repository.getActive();
      if (active == null) {
        state = base.copyWith(
          isMutating: false,
          errorMessage: fallbackMessage,
          clearBlockedActive: true,
        );
        return;
      }
      final timing = _timingForActiveSession(
        active,
        fallbackFocusMinutes: base.focusMinutes,
        fallbackBreakMinutes: base.breakMinutes,
      );
      state = base.copyWith(
        isMutating: false,
        clearError: true,
        blockedActiveSession: active,
        blockedElapsedSeconds: timing.elapsed,
        blockedRemainingSeconds: timing.remaining,
      );
    } catch (_) {
      state = base.copyWith(
        isMutating: false,
        errorMessage: fallbackMessage,
        clearBlockedActive: true,
      );
    }
  }

  /// Idle ekrandaki "Active Session" kartından çalışan oturuma dön.
  Future<void> resumeBlockedSession() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.isMutating) return;
    state = current.copyWith(isMutating: true, clearError: true);
    await restoreActiveSession();
    if (state is StudySessionReady) {
      final after = _ready;
      if (after.session != null && after.phase != PomodoroPhase.idle) {
        state = after.copyWith(
          isMutating: false,
          clearBlockedActive: true,
          clearError: true,
        );
      } else {
        state = current.copyWith(
          isMutating: false,
          errorMessage: 'Aktif oturum yüklenemedi',
        );
      }
    }
  }

  /// Server'daki aktif oturumu bitirir; ardından yeni Pomodoro başlatılabilir.
  Future<void> endBlockedSession() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.isMutating) return;

    if (current.session != null && current.phase != PomodoroPhase.idle) {
      await finish();
      return;
    }

    state = current.copyWith(isMutating: true, clearError: true);
    try {
      final active = current.blockedActiveSession ?? await _repository.getActive();
      if (active != null) {
        await _finish();
      }
      _ticker?.cancel();
      await _notifications.cancelAll();
      await _syncPomodoroWidget(isActive: false);
      state = StudySessionReady.idle(
        preset: PomodoroPreset(
          focusMinutes: current.focusMinutes,
          breakMinutes: current.breakMinutes,
          label: '${current.focusMinutes} / ${current.breakMinutes}',
        ),
        isChronometer: current.isChronometer,
      ).copyWith(
        subject: current.subject,
        topic: current.topic,
        subjectCode: current.subjectCode,
        topicCode: current.topicCode,
        studyPlanId: current.studyPlanId,
        clearBlockedActive: true,
        clearError: true,
      );
      await _syncLiveNotification(force: true);
      onSessionCompleted?.call();
    } on AppException catch (e) {
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Oturum bitirilemedi',
      );
    }
  }

  Future<void> takeBreak() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (!current.isRunning ||
        current.phase != PomodoroPhase.focus ||
        current.isMutating) {
      return;
    }
    state = current.copyWith(isMutating: true, clearError: true);
    try {
      final session = await _repository.startBreak();
      _ticker?.cancel();
      await _notifications.cancelAll();
      final breakSecs =
          current.breakMinutes > 0 ? current.breakMinutes * 60 : 5 * 60;
      state = current.copyWith(
        session: session,
        phase: PomodoroPhase.breakTime,
        isRunning: true,
        isMutating: false,
        remainingSeconds: breakSecs,
        elapsedSeconds: 0,
        savedFocusRemainingSeconds: current.remainingSeconds,
        savedFocusElapsedSeconds: current.elapsedSeconds,
      );
      _startTicker();
      await _syncLiveNotification(force: true);
    } on AppException catch (e) {
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Mola başlatılamadı',
      );
    }
  }

  Future<void> endServerBreak() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.phase != PomodoroPhase.breakTime || current.isMutating) return;
    state = current.copyWith(isMutating: true, clearError: true);
    try {
      final session = await _repository.endBreak();
      _ticker?.cancel();
      await _notifications.cancelAll();
      final remaining = current.isChronometer
          ? (current.savedFocusRemainingSeconds ?? current.savedFocusElapsedSeconds ?? 0)
          : (current.savedFocusRemainingSeconds ??
              (current.focusMinutes * 60)
                  .clamp(0, current.focusMinutes * 60));
      final elapsed = current.savedFocusElapsedSeconds ?? 0;
      state = current.copyWith(
        session: session,
        phase: PomodoroPhase.focus,
        isRunning: true,
        isMutating: false,
        remainingSeconds: remaining,
        elapsedSeconds: elapsed,
        clearSavedFocus: true,
      );
      _startTicker();
      await _syncLiveNotification(force: true);
    } on AppException catch (e) {
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Mola bitirilemedi',
      );
    }
  }

  Future<void> pause() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (!current.isRunning || current.isMutating) return;

    if (current.phase == PomodoroPhase.breakTime) {
      _ticker?.cancel();
      state = current.copyWith(isRunning: false);
      await _notifications.cancelAll();
      return;
    }

    state = current.copyWith(isMutating: true, clearError: true);
    try {
      final session = await _pause();
      _ticker?.cancel();
      await _notifications.cancelAll();
      state = current.copyWith(
        session: session,
        isRunning: false,
        isMutating: false,
      );
      await _syncPomodoroWidget(
        isActive: false,
        planTitle: current.subject ?? current.topic,
      );
      await _syncLiveNotification(force: true);
    } on AppException catch (e) {
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Duraklatma başarısız',
      );
    }
  }

  Future<void> resume() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.isRunning || current.isMutating) return;

    if (current.phase == PomodoroPhase.breakTime) {
      _startBreakTicker(current);
      return;
    }

    state = current.copyWith(isMutating: true, clearError: true);
    try {
      final session = await _resume();
      state = current.copyWith(
        session: session,
        isRunning: true,
        isMutating: false,
      );
      _startTicker();
      await _scheduleFocusEnd(Duration(seconds: current.remainingSeconds));
      await _syncPomodoroWidget(
        isActive: true,
        remainingLabel: _formatRemaining(current.remainingSeconds),
        planTitle: current.subject ?? current.topic,
      );
      await _syncLiveNotification(force: true);
    } on AppException catch (e) {
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Devam ettirme başarısız',
      );
    }
  }

  Future<void> finish({int? completedQuestions}) async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (current.isMutating) return;

    if (current.phase == PomodoroPhase.breakTime || current.session == null) {
      _ticker?.cancel();
      await _notifications.cancelAll();
      state = StudySessionReady.idle(
        preset: PomodoroPreset(
          focusMinutes: current.focusMinutes,
          breakMinutes: current.breakMinutes,
          label: '${current.focusMinutes} / ${current.breakMinutes}',
        ),
      ).copyWith(
        subject: current.subject,
        topic: current.topic,
        studyPlanId: current.studyPlanId,
      );
      await _syncLiveNotification(force: true);
      return;
    }

    state = current.copyWith(isMutating: true, clearError: true);
    try {
      await _finish(completedQuestions: completedQuestions);
      _ticker?.cancel();
      await _notifications.cancelAll();
      await _syncPomodoroWidget(isActive: false);
      state = StudySessionReady.idle(
        preset: PomodoroPreset(
          focusMinutes: current.focusMinutes,
          breakMinutes: current.breakMinutes,
          label: '${current.focusMinutes} / ${current.breakMinutes}',
        ),
      ).copyWith(
        subject: current.subject,
        topic: current.topic,
        studyPlanId: current.studyPlanId,
        clearBlockedActive: true,
      );
      await _syncLiveNotification(force: true);
      onSessionCompleted?.call();
    } on AppException catch (e) {
      state = current.copyWith(isMutating: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isMutating: false,
        errorMessage: 'Oturum bitirilemedi',
      );
    }
  }

  void _startTicker() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) => _onTick());
  }

  void _startBreakTicker(StudySessionReady current) {
    final remaining = current.phase == PomodoroPhase.breakTime &&
            current.remainingSeconds > 0
        ? current.remainingSeconds
        : current.breakMinutes * 60;
    state = current.copyWith(
      phase: PomodoroPhase.breakTime,
      isRunning: true,
      remainingSeconds: remaining,
      elapsedSeconds: 0,
      clearError: true,
    );
    _startTicker();
    if (_longBreakNotificationsEnabled()) {
      unawaited(
        _notifications.scheduleBreakEnd(after: Duration(seconds: remaining)),
      );
    }
  }

  Future<void> _scheduleFocusEnd(Duration after) async {
    if (!_pomodoroNotificationsEnabled()) return;
    await _notifications.scheduleFocusEnd(after: after);
  }

  String _formatRemaining(int totalSeconds) {
    final m = totalSeconds ~/ 60;
    final s = totalSeconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  Future<void> _syncPomodoroWidget({
    required bool isActive,
    String? remainingLabel,
    String? planTitle,
  }) async {
    final service = _widgetService;
    if (service == null) return;
    try {
      await service.updatePomodoroOverlay(
        isActive: isActive,
        remainingLabel: remainingLabel,
        planTitle: planTitle,
      );
    } catch (_) {
      // Widget senkronu oturumu bozmamalı.
    }
  }

  Future<void> _syncLiveNotification({bool force = false}) async {
    final live = _liveNotification;
    if (live == null || state is! StudySessionReady) return;
    final current = _ready;
    if (!force) {
      _liveSyncTick += 1;
      if (_liveSyncTick % 5 != 0) return;
    } else {
      _liveSyncTick = 0;
    }
    try {
      await live.syncFromEngine(
        engineState: current.engineState,
        subject: current.displaySubject,
        topic: current.displayTopic,
        elapsedHms: current.elapsedHmsLabel,
        nextSubject: current.displaySubject,
      );
    } catch (_) {
      // Kilit ekranı bildirimi oturumu bozmamalı.
    }
  }

  Future<void> _onTick() async {
    if (state is! StudySessionReady) return;
    final current = _ready;
    if (!current.isRunning) return;

    // Chronometer: count-up only (no auto-finish)
    if (current.isChronometer && current.phase == PomodoroPhase.focus) {
      state = current.copyWith(
        elapsedSeconds: current.elapsedSeconds + 1,
        remainingSeconds: current.elapsedSeconds + 1,
      );
      await _syncLiveNotification();
      return;
    }

    if (current.remainingSeconds <= 1) {
      _ticker?.cancel();
      if (current.phase == PomodoroPhase.focus) {
        if (_pomodoroNotificationsEnabled()) {
          await _notifications.showImmediate(
            title: 'Pomodoro tamamlandı',
            body: 'Odak süren bitti. Kısa bir mola zamanı!',
          );
        }
        try {
          await _finish();
          onSessionCompleted?.call();
        } on AppException {
          // Bildirim zaten gösterildi; UI idle'a düşmesin, molaya geçilsin.
        }
        if (current.breakMinutes > 0) {
          state = current.copyWith(
            phase: PomodoroPhase.breakTime,
            isRunning: true,
            remainingSeconds: current.breakMinutes * 60,
            elapsedSeconds: 0,
            clearSession: true,
            isMutating: false,
          );
          _startTicker();
          await _notifications.scheduleBreakEnd(
            after: Duration(minutes: current.breakMinutes),
          );
          await _syncLiveNotification(force: true);
        } else {
          state = StudySessionReady.idle(
            preset: PomodoroPreset(
              focusMinutes: current.focusMinutes,
              breakMinutes: current.breakMinutes,
              label: '${current.focusMinutes} / ${current.breakMinutes}',
            ),
          ).copyWith(
            subject: current.subject,
            topic: current.topic,
            studyPlanId: current.studyPlanId,
          );
          await _syncLiveNotification(force: true);
        }
      } else {
        await _notifications.showImmediate(
          title: 'Mola bitti',
          body: 'Hazırsan bir sonraki odak oturumuna başla.',
        );
        state = StudySessionReady.idle(
          preset: PomodoroPreset(
            focusMinutes: current.focusMinutes,
            breakMinutes: current.breakMinutes,
            label: '${current.focusMinutes} / ${current.breakMinutes}',
          ),
        ).copyWith(
          subject: current.subject,
          topic: current.topic,
          studyPlanId: current.studyPlanId,
        );
        await _syncLiveNotification(force: true);
      }
      return;
    }

    state = current.copyWith(
      remainingSeconds: current.remainingSeconds - 1,
      elapsedSeconds: current.elapsedSeconds + 1,
    );
    await _syncLiveNotification();
  }

  @override
  void dispose() {
    _ticker?.cancel();
    unawaited(_notifications.cancelAll());
    final live = _liveNotification;
    if (live != null) unawaited(live.clear());
    super.dispose();
  }
}

final studySessionProvider =
    StateNotifierProvider<StudySessionNotifier, StudySessionState>((ref) {
  bool pref(bool Function(NotificationSettingsLoaded s) pick) {
    final settings = ref.read(notificationSettingsProvider);
    if (settings is NotificationSettingsLoaded) return pick(settings);
    return true;
  }

  final live = ref.watch(studySessionLiveNotificationProvider);
  final notifier = StudySessionNotifier(
    start: ref.watch(_startUsecaseProvider),
    pause: ref.watch(_pauseUsecaseProvider),
    resume: ref.watch(_resumeUsecaseProvider),
    finish: ref.watch(_finishUsecaseProvider),
    repository: ref.watch(studySessionRepositoryProvider),
    notifications: ref.watch(pomodoroNotificationServiceProvider),
    liveNotification: live,
    widgetService: ref.watch(widgetServiceProvider),
    pomodoroNotificationsEnabled: () =>
        pref((s) => s.settings.pomodoroEnabled),
    longBreakNotificationsEnabled: () =>
        pref((s) => s.settings.longBreakEnabled),
    onSessionCompleted: () {
      ref.invalidate(dashboardProvider);
      ref.invalidate(statisticsProvider);
      ref.invalidate(studyPlanProvider);
      ref.invalidate(studySessionTodaySummaryProvider);
    },
  );
  live.setActionHandler(notifier.handleLiveNotificationAction);
  return notifier;
});
