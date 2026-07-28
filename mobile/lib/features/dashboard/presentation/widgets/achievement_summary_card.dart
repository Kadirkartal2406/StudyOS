import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-2.9 K1 — Rozet özeti
class AchievementSummaryCard extends StatelessWidget {
  const AchievementSummaryCard({
    super.key,
    this.totalUnlocked = 0,
    this.totalPoints = 0,
    this.recentTitle,
    this.recentReason,
  });

  final int totalUnlocked;
  final int totalPoints;
  final String? recentTitle;
  final String? recentReason;

  @override
  Widget build(BuildContext context) {
    if (totalUnlocked == 0) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.emoji_events_outlined),
          title: const Text('Henüz rozet yok'),
          trailing: TextButton(
            onPressed: () => context.push('/achievements'),
            child: const Text('Keşfet'),
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
                Icon(Icons.emoji_events, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Rozetler',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text('$totalUnlocked rozet · $totalPoints puan'),
            if (recentTitle != null) ...[
              const SizedBox(height: 4),
              Text('Son: $recentTitle'),
            ],
            if (recentReason != null && recentReason!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(recentReason!, style: Theme.of(context).textTheme.bodySmall),
            ],
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => context.push('/achievements'),
                child: const Text('Tümü'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
