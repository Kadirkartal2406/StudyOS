/// Achievement domain — Sprint-2.9 (S-33)
class AchievementEntity {
  const AchievementEntity({
    required this.id,
    required this.code,
    required this.title,
    required this.description,
    required this.category,
    required this.tier,
    required this.points,
    required this.iconKey,
    this.reason,
    this.unlockedAt,
    this.unlocked = false,
    this.currentValue = 0,
    this.targetValue = 1,
  });

  final String id;
  final String code;
  final String title;
  final String description;
  final String category;
  final String tier;
  final int points;
  final String iconKey;
  final String? reason;
  final DateTime? unlockedAt;
  final bool unlocked;
  final double currentValue;
  final double targetValue;
}

class AchievementExplainEntity {
  const AchievementExplainEntity({
    required this.achievementId,
    required this.explanation,
    required this.provider,
    required this.reason,
    required this.code,
    required this.title,
    this.usedFallback = false,
  });

  final String achievementId;
  final String explanation;
  final String provider;
  final String reason;
  final String code;
  final String title;
  final bool usedFallback;
}
