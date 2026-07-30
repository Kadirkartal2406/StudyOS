import 'package:flutter/material.dart';

/// Sprint 33 — Goal Progress Widget: Hedefe Uzaklık %XX + Rozet + Progress Bar
class GoalProgressBanner extends StatelessWidget {
  const GoalProgressBanner({
    super.key,
    required this.examLabel,
    this.progressPct = 62.0,
    this.badge = '🥈 Altın Hedef',
    this.targetNet = 85.0,
    this.currentNet = 52.7,
  });

  final String examLabel;
  final double progressPct;
  final String badge;
  final double targetNet;
  final double currentNet;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final pctInt = progressPct.clamp(0.0, 100.0).round();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      margin: const EdgeInsets.only(top: 10),
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: scheme.outlineVariant.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '$examLabel Hedefine Uzaklık',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: scheme.primary.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  badge,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: scheme.primary,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: progressPct / 100.0,
                    minHeight: 10,
                    backgroundColor: scheme.primary.withValues(alpha: 0.15),
                    valueColor: AlwaysStoppedAnimation<Color>(scheme.primary),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '%$pctInt',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                      color: scheme.primary,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Mevcut Net: ${currentNet.toStringAsFixed(1)} / Hedef Net: ${targetNet.toStringAsFixed(1)}',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
          ),
        ],
      ),
    );
  }
}
