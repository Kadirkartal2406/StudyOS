class GoalExplainEntity {
  const GoalExplainEntity({
    required this.goalId,
    required this.explanation,
    required this.whyProgressed,
    required this.whyStalled,
    required this.howToComplete,
    required this.title,
    required this.progress,
    this.provider,
    this.usedFallback = false,
  });

  final String goalId;
  final String explanation;
  final String whyProgressed;
  final String whyStalled;
  final String howToComplete;
  final String title;
  final double progress;
  final String? provider;
  final bool usedFallback;
}
