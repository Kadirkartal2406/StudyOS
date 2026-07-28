import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-3.1.B — Bugünkü plan özeti.
class DashboardPlanPreview extends StatelessWidget {
  const DashboardPlanPreview({
    super.key,
    required this.todayPlanCount,
    required this.completedPlanCount,
    this.todayStudiedTopic,
    this.plannerOverviewReason,
  });

  final int todayPlanCount;
  final int completedPlanCount;
  final String? todayStudiedTopic;
  final String? plannerOverviewReason;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'Plan',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => context.push('/study-plan'),
                  child: const Text('Detay'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              todayPlanCount == 0
                  ? 'Bugün için plan kaydı yok.'
                  : '$completedPlanCount / $todayPlanCount görev tamamlandı',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            if (todayStudiedTopic != null && todayStudiedTopic!.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                'Odak: $todayStudiedTopic',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
            if (plannerOverviewReason != null &&
                plannerOverviewReason!.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                plannerOverviewReason!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
