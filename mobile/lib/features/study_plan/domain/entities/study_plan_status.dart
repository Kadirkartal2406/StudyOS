/// Çalışma planı durumu — backend `StudyPlanStatus` enum'u ile eşleşir
/// (bkz. docs/architecture/database-design.md §1.9).
enum StudyPlanStatus {
  planned,
  inProgress,
  completed,
  skipped;

  static StudyPlanStatus fromApi(String value) {
    return switch (value) {
      'planned' => StudyPlanStatus.planned,
      'in_progress' => StudyPlanStatus.inProgress,
      'completed' => StudyPlanStatus.completed,
      'skipped' => StudyPlanStatus.skipped,
      _ => throw ArgumentError('Bilinmeyen plan durumu: $value'),
    };
  }

  bool get isTerminal => this == completed || this == skipped;
}
