/// Pomodoro oturumu durumu — backend `StudySessionStatus` ile uyumlu.
enum StudySessionStatus {
  running,
  paused,
  completed;

  static StudySessionStatus fromApi(String value) {
    return switch (value) {
      'running' => StudySessionStatus.running,
      'paused' => StudySessionStatus.paused,
      'completed' => StudySessionStatus.completed,
      _ => StudySessionStatus.completed,
    };
  }

  String get apiValue => name;

  bool get isActive =>
      this == StudySessionStatus.running || this == StudySessionStatus.paused;
}
