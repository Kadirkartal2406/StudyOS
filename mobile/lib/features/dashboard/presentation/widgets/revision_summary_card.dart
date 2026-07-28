import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-2.8 K1 — Bugünkü tekrar özeti
class RevisionSummaryCard extends StatelessWidget {
  const RevisionSummaryCard({
    super.key,
    this.dueToday = 0,
    this.overdue = 0,
    this.dueThisWeek = 0,
    this.nextTitle,
    this.overviewReason,
  });

  final int dueToday;
  final int overdue;
  final int dueThisWeek;
  final String? nextTitle;
  final String? overviewReason;

  @override
  Widget build(BuildContext context) {
    if (dueToday == 0 && overdue == 0 && dueThisWeek == 0) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.replay_circle_filled_outlined),
          title: const Text('Bugün tekrar yok'),
          trailing: TextButton(
            onPressed: () => context.push('/revisions'),
            child: const Text('Aç'),
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
                  Icons.replay_circle_filled,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Bugünkü Tekrarlar',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Bugün $dueToday · Gecikmiş $overdue · Bu hafta $dueThisWeek',
            ),
            if (nextTitle != null) ...[
              const SizedBox(height: 4),
              Text('Sıradaki: $nextTitle'),
            ],
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
                onPressed: () => context.push('/revisions'),
                child: const Text('Görüntüle'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
