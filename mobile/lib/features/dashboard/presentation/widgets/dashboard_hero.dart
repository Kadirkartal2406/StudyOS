import 'package:flutter/material.dart';

import '../../domain/entities/dashboard_entity.dart';
import 'active_exam_switcher.dart';
import 'dashboard_layout_strategy.dart';

/// Sprint-3.1.B — Journey Hub Hero.
class DashboardHero extends StatelessWidget {
  const DashboardHero({
    super.key,
    required this.firstName,
    required this.primaryTarget,
    required this.activeExamType,
    required this.todayPct,
    required this.weekPct,
    required this.monthPct,
    this.daysRemaining,
    this.journeyStage,
  });

  final String firstName;
  final DashboardExamTargetEntity? primaryTarget;
  final String? activeExamType;
  final double todayPct;
  final double weekPct;
  final double monthPct;
  final int? daysRemaining;
  final String? journeyStage;

  @override
  Widget build(BuildContext context) {
    final strategy = dashboardLayoutFor(activeExamType);
    final colorScheme = Theme.of(context).colorScheme;
    final targetLine = strategy.formatPrimaryTarget(primaryTarget);

    return Card(
      elevation: 0,
      color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.45),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    firstName.isEmpty ? 'Merhaba' : 'Merhaba, $firstName',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
                const ActiveExamSwitcher(),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              targetLine,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            if (journeyStage != null && journeyStage!.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                'Aşama: ${_stageLabel(journeyStage!)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
            const SizedBox(height: 16),
            _ProgressRow(label: 'Günlük', value: todayPct),
            const SizedBox(height: 8),
            _ProgressRow(label: 'Haftalık', value: weekPct),
            const SizedBox(height: 8),
            _ProgressRow(label: 'Aylık', value: monthPct),
            if (daysRemaining != null) ...[
              const SizedBox(height: 14),
              Text(
                daysRemaining! > 0
                    ? 'Sınava $daysRemaining gün kaldı'
                    : 'Sınav tarihi yaklaşıyor',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: colorScheme.primary,
                    ),
              ),
            ],
            if (strategy.focusLabels().isNotEmpty) ...[
              const SizedBox(height: 10),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: [
                  for (final label in strategy.focusLabels())
                    Chip(
                      label: Text(label),
                      visualDensity: VisualDensity.compact,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  static String _stageLabel(String stage) {
    return switch (stage) {
      'onboarding' => 'Kurulum',
      'foundation' => 'Temel',
      'building' => 'İnşa',
      'acceleration' => 'Hızlanma',
      'peak' => 'Zirve',
      'learning' => 'Öğrenme',
      _ => stage,
    };
  }
}

class _ProgressRow extends StatelessWidget {
  const _ProgressRow({required this.label, required this.value});

  final String label;
  final double value;

  @override
  Widget build(BuildContext context) {
    final pct = (value.clamp(0, 100)) / 100;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(child: Text(label)),
            Text('${value.clamp(0, 100).toStringAsFixed(0)}%'),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(value: pct),
      ],
    );
  }
}
