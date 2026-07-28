/// Ürün hedef tipleri — kullanıcıya gösterilir (Sprint-3.0.2).
/// Motor GoalType arka planda kalır.
enum ProductGoalType {
  dailyStudyTime,
  dailyQuestions,
  weeklyQuestions,
  netTarget,
  scoreTarget,
  rankTarget,
  branchNet,
  examCount,
  revisionTarget;

  String get apiValue => switch (this) {
        ProductGoalType.dailyStudyTime => 'daily_study_time',
        ProductGoalType.dailyQuestions => 'daily_questions',
        ProductGoalType.weeklyQuestions => 'weekly_questions',
        ProductGoalType.netTarget => 'net_target',
        ProductGoalType.scoreTarget => 'score_target',
        ProductGoalType.rankTarget => 'rank_target',
        ProductGoalType.branchNet => 'branch_net',
        ProductGoalType.examCount => 'exam_count',
        ProductGoalType.revisionTarget => 'revision_target',
      };

  static ProductGoalType? fromApi(String? value) {
    if (value == null || value.isEmpty) return null;
    return switch (value) {
      'daily_study_time' => ProductGoalType.dailyStudyTime,
      'daily_questions' => ProductGoalType.dailyQuestions,
      'weekly_questions' => ProductGoalType.weeklyQuestions,
      'net_target' => ProductGoalType.netTarget,
      'score_target' => ProductGoalType.scoreTarget,
      'rank_target' => ProductGoalType.rankTarget,
      'branch_net' => ProductGoalType.branchNet,
      'exam_count' => ProductGoalType.examCount,
      'revision_target' => ProductGoalType.revisionTarget,
      _ => null,
    };
  }

  String get label => switch (this) {
        ProductGoalType.dailyStudyTime => 'Günlük Çalışma Süresi',
        ProductGoalType.dailyQuestions => 'Günlük Soru Sayısı',
        ProductGoalType.weeklyQuestions => 'Haftalık Soru Sayısı',
        ProductGoalType.netTarget => 'Net Hedefi',
        ProductGoalType.scoreTarget => 'Puan Hedefi',
        ProductGoalType.rankTarget => 'Sıralama Hedefi',
        ProductGoalType.branchNet => 'Branş Neti',
        ProductGoalType.examCount => 'Deneme Sayısı',
        ProductGoalType.revisionTarget => 'Revision Hedefi',
      };

  String get targetLabel => switch (this) {
        ProductGoalType.dailyStudyTime => 'Dakika',
        ProductGoalType.dailyQuestions => 'Soru sayısı',
        ProductGoalType.weeklyQuestions => 'Soru sayısı',
        ProductGoalType.netTarget => 'Hedef net',
        ProductGoalType.scoreTarget => 'Hedef puan',
        ProductGoalType.rankTarget => 'Hedef sıralama',
        ProductGoalType.branchNet => 'Hedef net',
        ProductGoalType.examCount => 'Deneme sayısı',
        ProductGoalType.revisionTarget => 'Tekrar sayısı',
      };

  bool get requiresSubject =>
      this == ProductGoalType.branchNet || this == ProductGoalType.revisionTarget;

  bool get showSubject =>
      this == ProductGoalType.branchNet ||
      this == ProductGoalType.revisionTarget ||
      this == ProductGoalType.netTarget;
}
