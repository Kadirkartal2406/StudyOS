import '../../domain/entities/pomodoro_preset.dart';
import '../../domain/entities/study_session_entity.dart';
import '../../domain/entities/study_session_status.dart';

/// Pomodoro ekranının istemci tarafı fazı.
enum PomodoroPhase {
  idle,
  focus,
  breakTime,
}

/// Study session / Pomodoro UI durumu.
sealed class StudySessionState {
  const StudySessionState();
}

final class StudySessionInitial extends StudySessionState {
  const StudySessionInitial();
}

final class StudySessionReady extends StudySessionState {
  const StudySessionReady({
    required this.focusMinutes,
    required this.breakMinutes,
    required this.remainingSeconds,
    required this.elapsedSeconds,
    required this.phase,
    required this.isRunning,
    required this.isMutating,
    this.isChronometer = false,
    this.savedFocusRemainingSeconds,
    this.savedFocusElapsedSeconds,
    this.session,
    this.subject,
    this.topic,
    this.subjectCode,
    this.topicCode,
    this.studyPlanId,
    this.errorMessage,
    this.blockedActiveSession,
    this.blockedElapsedSeconds = 0,
    this.blockedRemainingSeconds = 0,
  });

  final int focusMinutes;
  final int breakMinutes;
  final int remainingSeconds;
  final int elapsedSeconds;
  final PomodoroPhase phase;
  final bool isRunning;
  final bool isMutating;
  /// Serbest kronometre (count-up); false = pomodoro countdown.
  final bool isChronometer;
  /// Mid-session mola öncesi odak kalan/geçen süre (geri dönüş için).
  final int? savedFocusRemainingSeconds;
  final int? savedFocusElapsedSeconds;
  final StudySessionEntity? session;
  final String? subject;
  final String? topic;
  /// LOS: Evidence binding için canonical kodlar
  final String? subjectCode;
  final String? topicCode;
  final String? studyPlanId;
  final String? errorMessage;
  /// Server'da aktif oturum var ama yerel faz hâlâ idle (409 sonrası).
  final StudySessionEntity? blockedActiveSession;
  final int blockedElapsedSeconds;
  final int blockedRemainingSeconds;

  bool get hasBlockedActiveSession => blockedActiveSession != null;

  String get blockedSessionTitle {
    final s = blockedActiveSession;
    if (s == null) return 'Aktif oturum';
    final subject = s.planSubject ?? s.subjectCode;
    final topic = s.planTitle ?? s.topicCode;
    if (subject != null && subject.isNotEmpty) {
      if (topic != null && topic.isNotEmpty) return '$subject · $topic';
      return subject;
    }
    if (topic != null && topic.isNotEmpty) return topic;
    return s.mode == 'chronometer' ? 'Kronometre' : 'Pomodoro';
  }

  String get blockedSessionStateLabel {
    final s = blockedActiveSession;
    if (s == null) return '';
    if (s.status == StudySessionStatus.paused) return 'Paused';
    if (s.isBreak) return 'Break';
    return 'Focus';
  }

  String get blockedElapsedLabel => _mmss(blockedElapsedSeconds);
  String get blockedRemainingLabel => _mmss(blockedRemainingSeconds);

  static String _mmss(int total) {
    final m = total ~/ 60;
    final s = total % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  int get totalSeconds {
    if (phase == PomodoroPhase.breakTime) {
      return breakMinutes * 60;
    }
    return focusMinutes * 60;
  }

  double get progress {
    final total = totalSeconds;
    if (total <= 0) return 0;
    return ((total - remainingSeconds) / total).clamp(0.0, 1.0);
  }

  String get remainingLabel {
    final m = remainingSeconds ~/ 60;
    final s = remainingSeconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  String get elapsedLabel {
    final m = elapsedSeconds ~/ 60;
    final s = elapsedSeconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  /// HH:MM:SS — dashboard / kilit ekranı kartı.
  String get elapsedHmsLabel {
    final h = elapsedSeconds ~/ 3600;
    final m = (elapsedSeconds % 3600) ~/ 60;
    final s = elapsedSeconds % 60;
    return '${h.toString().padLeft(2, '0')}:'
        '${m.toString().padLeft(2, '0')}:'
        '${s.toString().padLeft(2, '0')}';
  }

  /// M25 engine state projection.
  StudyEngineState get engineState {
    if (session?.status == StudySessionStatus.completed) {
      return StudyEngineState.completed;
    }
    if (phase == PomodoroPhase.breakTime) return StudyEngineState.breakTime;
    if (session?.status == StudySessionStatus.paused ||
        (session != null &&
            !isRunning &&
            phase == PomodoroPhase.focus)) {
      return StudyEngineState.paused;
    }
    if (phase == PomodoroPhase.focus && (isRunning || session != null)) {
      return StudyEngineState.studying;
    }
    return StudyEngineState.idle;
  }

  bool get isLiveSession =>
      engineState == StudyEngineState.studying ||
      engineState == StudyEngineState.breakTime ||
      engineState == StudyEngineState.paused;

  String get displaySubject =>
      subject ?? session?.planSubject ?? session?.subjectCode ?? 'Serbest';

  String get displayTopic =>
      topic ?? session?.planTitle ?? session?.topicCode ?? '';

  StudySessionReady copyWith({
    int? focusMinutes,
    int? breakMinutes,
    int? remainingSeconds,
    int? elapsedSeconds,
    PomodoroPhase? phase,
    bool? isRunning,
    bool? isMutating,
    bool? isChronometer,
    int? savedFocusRemainingSeconds,
    int? savedFocusElapsedSeconds,
    StudySessionEntity? session,
    String? subject,
    String? topic,
    String? subjectCode,
    String? topicCode,
    String? studyPlanId,
    String? errorMessage,
    StudySessionEntity? blockedActiveSession,
    int? blockedElapsedSeconds,
    int? blockedRemainingSeconds,
    bool clearSession = false,
    bool clearError = false,
    bool clearSavedFocus = false,
    bool clearBlockedActive = false,
  }) {
    return StudySessionReady(
      focusMinutes: focusMinutes ?? this.focusMinutes,
      breakMinutes: breakMinutes ?? this.breakMinutes,
      remainingSeconds: remainingSeconds ?? this.remainingSeconds,
      elapsedSeconds: elapsedSeconds ?? this.elapsedSeconds,
      phase: phase ?? this.phase,
      isRunning: isRunning ?? this.isRunning,
      isMutating: isMutating ?? this.isMutating,
      isChronometer: isChronometer ?? this.isChronometer,
      savedFocusRemainingSeconds: clearSavedFocus
          ? null
          : (savedFocusRemainingSeconds ?? this.savedFocusRemainingSeconds),
      savedFocusElapsedSeconds: clearSavedFocus
          ? null
          : (savedFocusElapsedSeconds ?? this.savedFocusElapsedSeconds),
      session: clearSession ? null : (session ?? this.session),
      subject: subject ?? this.subject,
      topic: topic ?? this.topic,
      subjectCode: subjectCode ?? this.subjectCode,
      topicCode: topicCode ?? this.topicCode,
      studyPlanId: studyPlanId ?? this.studyPlanId,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      blockedActiveSession: clearBlockedActive
          ? null
          : (blockedActiveSession ?? this.blockedActiveSession),
      blockedElapsedSeconds: clearBlockedActive
          ? 0
          : (blockedElapsedSeconds ?? this.blockedElapsedSeconds),
      blockedRemainingSeconds: clearBlockedActive
          ? 0
          : (blockedRemainingSeconds ?? this.blockedRemainingSeconds),
    );
  }

  static StudySessionReady idle({
    PomodoroPreset preset = const PomodoroPreset(
      focusMinutes: 25,
      breakMinutes: 5,
      label: '25 / 5',
    ),
    bool isChronometer = false,
  }) {
    return StudySessionReady(
      focusMinutes: preset.focusMinutes,
      breakMinutes: preset.breakMinutes,
      remainingSeconds: isChronometer ? 0 : preset.focusMinutes * 60,
      elapsedSeconds: 0,
      phase: PomodoroPhase.idle,
      isRunning: false,
      isMutating: false,
      isChronometer: isChronometer,
    );
  }
}

final class StudySessionError extends StudySessionState {
  const StudySessionError(this.message);

  final String message;
}
