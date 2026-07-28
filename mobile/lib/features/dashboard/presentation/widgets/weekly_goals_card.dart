import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../goal_engine/presentation/widgets/goal_progress_bar.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Dashboard — Bu Haftaki Hedefler (Sprint-2.1 / 3.0.2).
class WeeklyGoalsCard extends StatelessWidget {
  const WeeklyGoalsCard({super.key, required this.weeklyGoals});

  final List<WeeklyGoalSummaryEntity> weeklyGoals;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/goals'),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.flag_circle_outlined,
                    color: colorScheme.primary,
                    size: 22,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Bu Haftaki Hedefler',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  Icon(
                    Icons.chevron_right_rounded,
                    color: colorScheme.onSurfaceVariant,
                  ),
                ],
              ),
              const SizedBox(height: 12),
              if (weeklyGoals.isEmpty)
                Text(
                  'Bu hafta için hedef yok. Hedefler ekranından ekleyebilirsin.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                )
              else
                ...weeklyGoals.take(3).map((goal) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: InkWell(
                      onTap: () => context.push('/goals/${goal.id}'),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            goal.title,
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 6),
                          GoalProgressBar(
                            progress: goal.progress,
                            showLabel: false,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '%${goal.progress.toStringAsFixed(0)} · '
                            '${goal.currentValue.toStringAsFixed(0)}/'
                            '${goal.targetValue.toStringAsFixed(0)} · '
                            'Kalan: ${goal.remaining.toStringAsFixed(0)}'
                            '${goal.estimatedCompletion != null && goal.estimatedCompletion!.isNotEmpty ? ' · ${goal.estimatedCompletion}' : (goal.etaHint != null && goal.etaHint!.isNotEmpty ? ' · ${goal.etaHint}' : '')}',
                            style: Theme.of(context)
                                .textTheme
                                .bodySmall
                                ?.copyWith(
                                  color: colorScheme.onSurfaceVariant,
                                ),
                          ),
                        ],
                      ),
                    ),
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }
}
