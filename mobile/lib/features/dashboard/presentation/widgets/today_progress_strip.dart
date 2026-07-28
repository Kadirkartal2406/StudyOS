import 'package:flutter/material.dart';

/// Alignment Sprint-1 — günlük ilerleme (CTA değil).
class TodayProgressStrip extends StatelessWidget {
  const TodayProgressStrip({
    super.key,
    required this.todayMinutes,
    required this.goalMinutes,
    required this.progressPercentage,
    this.streakDays,
  });

  final int todayMinutes;
  final int goalMinutes;
  final double progressPercentage;
  final int? streakDays;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final streak = streakDays ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                'Bugün $todayMinutes / $goalMinutes dk',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ),
            if (streak > 0)
              Text(
                '🔥 $streak gün seri',
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: colorScheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: (progressPercentage.clamp(0, 100)) / 100,
            minHeight: 8,
            backgroundColor: colorScheme.surfaceContainerHighest,
          ),
        ),
      ],
    );
  }
}
