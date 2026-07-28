import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/goal_entity.dart';
import 'goal_progress_bar.dart';

class GoalCard extends StatelessWidget {
  const GoalCard({super.key, required this.goal});

  final GoalEntity goal;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/goals/${goal.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      goal.title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  Chip(
                    label: Text(goal.status.label),
                    visualDensity: VisualDensity.compact,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                '${goal.displayTypeLabel} · ${goal.period.label} · ${goal.priority.label}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
              const SizedBox(height: 12),
              GoalProgressBar(progress: goal.progress),
              const SizedBox(height: 8),
              Text(
                '${goal.currentValue.toStringAsFixed(0)} / '
                '${goal.targetValue.toStringAsFixed(0)} · '
                'Kalan: ${goal.remaining.toStringAsFixed(0)}'
                '${goal.estimatedCompletion != null ? ' · ${goal.estimatedCompletion}' : ''}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
