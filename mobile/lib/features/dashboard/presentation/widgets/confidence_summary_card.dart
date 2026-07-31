import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../domain/entities/dashboard_entity.dart';

/// LOS Hizalama — Dashboard Confidence Özeti Kartı.
/// En düşük 3 TopicConfidence değerini renk kodlu bar olarak gösterir.
class ConfidenceSummaryCard extends StatelessWidget {
  const ConfidenceSummaryCard({super.key, required this.items});

  final List<TopicConfidenceSummaryEntity> items;

  Color _levelColor(BuildContext context, String level) {
    final theme = Theme.of(context);
    switch (level) {
      case 'low':
        return theme.colorScheme.error;
      case 'medium':
        return Colors.orange;
      case 'high':
        return Colors.green;
      case 'conflicted':
        return Colors.amber;
      default:
        return theme.colorScheme.onSurfaceVariant;
    }
  }

  String _levelLabel(String level) {
    switch (level) {
      case 'low':
        return 'Düşük Güven';
      case 'medium':
        return 'Orta Seviye';
      case 'high':
        return 'Yüksek Güven';
      case 'conflicted':
        return 'Çelişkili';
      default:
        return 'Bilinmiyor';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const SizedBox.shrink();

    final theme = Theme.of(context);

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: AppSpacing.lg),
      color: theme.colorScheme.surfaceContainerLow,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.psychology_outlined,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Konu Odak Özeti (Inanç & Belirsizlik)',
                  style: theme.textTheme.labelLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: theme.colorScheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...items.map((item) {
              final color = _levelColor(context, item.confidenceLevel);
              final pct = (item.belief * 100).clamp(0, 100).toInt();

              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            item.displayName,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '${_levelLabel(item.confidenceLevel)} (%$pct)',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: color,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: item.belief.clamp(0.05, 1.0),
                        minHeight: 6,
                        backgroundColor:
                            theme.colorScheme.outlineVariant.withValues(alpha: 0.3),
                        valueColor: AlwaysStoppedAnimation<Color>(color),
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
