import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-2.5 — Bugünkü / tamamlanan / son kaynaklar özeti.
class TodayResourcesCard extends StatelessWidget {
  const TodayResourcesCard({
    super.key,
    required this.todayOpened,
    required this.todayCompleted,
    required this.recentTitles,
  });

  final int todayOpened;
  final int todayCompleted;
  final List<String> recentTitles;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.library_books_outlined, color: scheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Öğrenme Kaynakları',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => context.push('/resources'),
                  child: const Text('Tümü'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text('Bugün açılan: $todayOpened'),
            Text('Bugün tamamlanan: $todayCompleted'),
            if (recentTitles.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Son eklenenler',
                style: Theme.of(context).textTheme.labelLarge,
              ),
              ...recentTitles.take(3).map((t) => Text('· $t')),
            ],
          ],
        ),
      ),
    );
  }
}
