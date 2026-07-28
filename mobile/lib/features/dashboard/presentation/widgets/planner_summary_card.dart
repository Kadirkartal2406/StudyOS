import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-2.7 — demote kart (Today'de yok). AS-4 Suggest dili.
class PlannerSummaryCard extends StatelessWidget {
  const PlannerSummaryCard({
    super.key,
    this.draftId,
    this.status,
    this.targetExam,
    this.targetNet,
    this.itemCount = 0,
    this.overviewReason,
  });

  final String? draftId;
  final String? status;
  final String? targetExam;
  final double? targetNet;
  final int itemCount;
  final String? overviewReason;

  @override
  Widget build(BuildContext context) {
    if (draftId == null) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.auto_awesome_outlined),
          title: const Text('Bu hafta öneri yok'),
          trailing: TextButton(
            onPressed: () => context.push('/planner'),
            child: const Text('Öneriye bak'),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Önerilen çalışma planı',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '${(targetExam ?? '').toUpperCase()} · '
              'Hedef ${(targetNet ?? 0).toStringAsFixed(0)} net · '
              '$itemCount blok · ${status ?? 'draft'}',
            ),
            if (overviewReason != null && overviewReason!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                overviewReason!,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => context.push('/planner'),
                child: const Text('Görüntüle'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
