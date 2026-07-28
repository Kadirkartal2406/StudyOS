import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/ds.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Sprint 20 — Today Coach Card (Experience; Decision değil).
class TodayCoachCard extends StatelessWidget {
  const TodayCoachCard({super.key, required this.message});

  final CoachTodayEntity message;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return StudyCard(
      padding: AppSpacing.cardComfortable,
      color: scheme.tertiaryContainer.withValues(alpha: 0.35),
      borderColor: scheme.tertiary.withValues(alpha: 0.25),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology_outlined, color: scheme.tertiary, size: 20),
              const SizedBox(width: AppSpacing.xs),
              Text(
                'Koçun',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: scheme.tertiary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            message.headline,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(message.body, style: Theme.of(context).textTheme.bodyMedium),
          if (message.habitHint != null && message.habitHint!.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              message.habitHint!,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: scheme.onSurfaceVariant,
                  ),
            ),
          ],
          if (message.winTitle != null) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              '✦ ${message.winTitle}: ${message.winMessage ?? ''}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ],
          if (message.reasons.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Neden: ${message.reasons.take(2).join(' · ')}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
          if (message.deepLinkHint != null &&
              message.deepLinkHint!.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.md),
            FilledButton(
              onPressed: () => context.push(message.deepLinkHint!),
              child: Text(message.ctaLabel),
            ),
          ],
        ],
      ),
    );
  }
}
