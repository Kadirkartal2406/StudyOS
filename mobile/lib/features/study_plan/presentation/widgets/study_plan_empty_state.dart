import 'package:flutter/material.dart';

/// Alignment Sprint-4 — boş gün: önerilen plan veya Today.
class StudyPlanEmptyState extends StatelessWidget {
  const StudyPlanEmptyState({
    super.key,
    required this.onGoToToday,
    this.onSuggestPlan,
  });

  final VoidCallback onGoToToday;
  final VoidCallback? onSuggestPlan;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.event_note_rounded,
              size: 56,
              color: colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 16),
            Text(
              'Bugün için blok yok',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Önerilen çalışma planı oluşturabilir veya Today üzerinden devam edebilirsin.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 20),
            if (onSuggestPlan != null) ...[
              FilledButton.icon(
                onPressed: onSuggestPlan,
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Önerilen plan oluştur'),
              ),
              const SizedBox(height: 12),
            ],
            OutlinedButton.icon(
              onPressed: onGoToToday,
              icon: const Icon(Icons.today_rounded),
              label: const Text("Today'e git"),
            ),
          ],
        ),
      ),
    );
  }
}
