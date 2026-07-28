import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Dashboard — Bugünün AI Önerisi (Sprint-2.0, C1 additive).
class TodayAiRecommendationCard extends StatelessWidget {
  const TodayAiRecommendationCard({
    super.key,
    this.recommendation,
    this.recommendationCode,
  });

  final String? recommendation;
  final String? recommendationCode;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final message = recommendation?.trim();
    final hasMessage = message != null && message.isNotEmpty;

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/ai-chat'),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.auto_awesome_rounded,
                    color: colorScheme.primary,
                    size: 22,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Bugünün AI Önerisi',
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
              Text(
                hasMessage
                    ? message
                    : 'AI koçunu açarak çalışma önerilerini gör.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              if (recommendationCode != null &&
                  recommendationCode!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  recommendationCode!,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
