/// Hazır Pomodoro süre paketi (odak / mola, dakika).
class PomodoroPreset {
  const PomodoroPreset({
    required this.focusMinutes,
    required this.breakMinutes,
    required this.label,
  });

  final int focusMinutes;
  final int breakMinutes;
  final String label;

  static const List<PomodoroPreset> defaults = [
    PomodoroPreset(focusMinutes: 25, breakMinutes: 5, label: '25 / 5'),
    PomodoroPreset(focusMinutes: 50, breakMinutes: 10, label: '50 / 10'),
    PomodoroPreset(focusMinutes: 90, breakMinutes: 15, label: '90 / 15'),
  ];
}
