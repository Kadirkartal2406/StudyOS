import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-3.1.B — AI tip + RuleEngine reason (LLM Explain yok → 3.1.D).
class DashboardAiCoach extends StatelessWidget {
  const DashboardAiCoach({
    super.key,
    this.recommendation,
    this.reason,
  });

  final String? recommendation;
  final String? reason;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final tip = recommendation?.trim();
    final evidence = reason?.trim();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'AI Coach',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => context.push('/ai-coach'),
                  child: const Text('Koç'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              tip == null || tip.isEmpty
                  ? 'Bugün için henüz öneri yok.'
                  : tip,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            if (evidence != null && evidence.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Sebep: $evidence',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
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
