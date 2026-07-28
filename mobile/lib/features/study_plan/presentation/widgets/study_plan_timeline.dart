import 'package:flutter/material.dart';

import '../../domain/entities/study_plan_entity.dart';
import '../../domain/entities/study_plan_status.dart';

/// Saat aralığı tanımlı planları kronolojik sırada gösteren zaman çizelgesi.
/// Saati olmayan planlar (order_index ile sıralanan) ana listede kalır.
class StudyPlanTimeline extends StatelessWidget {
  const StudyPlanTimeline({super.key, required this.plans});

  final List<StudyPlanEntity> plans;

  @override
  Widget build(BuildContext context) {
    final scheduled = plans.where((p) => p.hasTimeRange).toList()
      ..sort(
        (a, b) => a.plannedStartTime!.totalMinutes.compareTo(
          b.plannedStartTime!.totalMinutes,
        ),
      );

    if (scheduled.isEmpty) return const SizedBox.shrink();

    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.view_timeline_outlined,
                  color: colorScheme.primary,
                  size: 22,
                ),
                const SizedBox(width: 8),
                Text(
                  'Zaman Çizelgesi',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            for (var i = 0; i < scheduled.length; i++)
              _TimelineRow(
                plan: scheduled[i],
                isLast: i == scheduled.length - 1,
              ),
          ],
        ),
      ),
    );
  }
}

class _TimelineRow extends StatelessWidget {
  const _TimelineRow({required this.plan, required this.isLast});

  final StudyPlanEntity plan;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final dotColor = switch (plan.status) {
      StudyPlanStatus.completed => Colors.green,
      StudyPlanStatus.skipped => colorScheme.error,
      StudyPlanStatus.inProgress => colorScheme.primary,
      StudyPlanStatus.planned => colorScheme.outline,
    };

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 52,
            child: Text(
              plan.plannedStartTime!.label,
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
          ),
          Column(
            children: [
              Container(
                width: 10,
                height: 10,
                margin: const EdgeInsets.only(top: 4),
                decoration:
                    BoxDecoration(color: dotColor, shape: BoxShape.circle),
              ),
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    margin: const EdgeInsets.symmetric(vertical: 2),
                    color: colorScheme.outlineVariant,
                  ),
                ),
            ],
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    plan.title,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                  Text(
                    '${plan.subject} · ${plan.plannedEndTime!.label}\'e kadar',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
