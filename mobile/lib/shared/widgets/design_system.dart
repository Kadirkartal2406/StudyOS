import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';
import 'study_card.dart';

/// Sprint 16 — Empty state (icon + title + body + optional CTA).
class EmptyState extends StatelessWidget {
  const EmptyState({
    super.key,
    required this.title,
    required this.message,
    this.icon = Icons.inbox_outlined,
    this.ctaLabel,
    this.onCta,
  });

  final String title;
  final String message;
  final IconData icon;
  final String? ctaLabel;
  final VoidCallback? onCta;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.lg),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: scheme.primaryContainer.withValues(alpha: 0.55),
              borderRadius: AppRadius.card,
            ),
            child: Icon(icon, color: scheme.primary),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            title,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: AppSpacing.xxs),
          Text(
            message,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
          ),
          if (ctaLabel != null && onCta != null) ...[
            const SizedBox(height: AppSpacing.md),
            FilledButton.tonal(onPressed: onCta, child: Text(ctaLabel!)),
          ],
        ],
      ),
    );
  }
}

/// Sprint 16 — Insight / soft recommendation card.
class InsightCardWidget extends StatelessWidget {
  const InsightCardWidget({
    super.key,
    required this.message,
    this.tone = 'neutral',
    this.onTap,
  });

  final String message;
  final String tone;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final color = AppColors.toneOf(tone);
    return StudyCard(
      onTap: onTap,
      padding: const EdgeInsets.all(AppSpacing.sm),
      color: color.withValues(alpha: 0.08),
      borderColor: color.withValues(alpha: 0.22),
      child: Row(
        children: [
          Icon(Icons.lightbulb_outline, size: 18, color: color),
          const SizedBox(width: AppSpacing.xs),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}

/// Sprint 16 — Topic intelligence summary card.
class IntelligenceCardWidget extends StatelessWidget {
  const IntelligenceCardWidget({
    super.key,
    required this.headline,
    required this.stars,
    required this.rows,
    this.suggestion,
    this.confidenceChip,
  });

  final String headline;
  final int stars;
  final List<(String, String)> rows;
  final String? suggestion;
  final Widget? confidenceChip;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final starText = '★' * stars.clamp(0, 5) + '☆' * (5 - stars.clamp(0, 5));
    return StudyCard(
      padding: AppSpacing.cardComfortable,
      color: scheme.surfaceContainerHighest.withValues(alpha: 0.45),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  headline,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
              ),
              if (confidenceChip != null) confidenceChip!,
            ],
          ),
          const SizedBox(height: AppSpacing.xxs),
          Text(
            starText,
            style: TextStyle(
              color: scheme.primary,
              letterSpacing: 2,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          ...rows.map(
            (r) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  SizedBox(
                    width: 110,
                    child: Text(
                      r.$1,
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: scheme.onSurfaceVariant,
                          ),
                    ),
                  ),
                  Expanded(child: Text(r.$2)),
                ],
              ),
            ),
          ),
          if (suggestion != null && suggestion!.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.xs),
            Text(
              'Öneri: $suggestion',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ],
        ],
      ),
    );
  }
}

/// Sprint 16 — Timeline row.
class TimelineTile extends StatelessWidget {
  const TimelineTile({
    super.key,
    required this.title,
    required this.relativeLabel,
    this.subtitle,
    this.icon = Icons.history,
    this.onTap,
  });

  final String title;
  final String relativeLabel;
  final String? subtitle;
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      dense: true,
      leading: Icon(icon, size: 20),
      title: Text(title),
      subtitle: subtitle == null ? null : Text(subtitle!),
      trailing: Text(
        relativeLabel,
        style: Theme.of(context).textTheme.labelSmall,
      ),
      onTap: onTap,
    );
  }
}

/// Sprint 16 — Feed / metric list tile in a card.
class MetricTile extends StatelessWidget {
  const MetricTile({
    super.key,
    required this.title,
    required this.subtitle,
    this.onTap,
    this.leading,
  });

  final String title;
  final String subtitle;
  final VoidCallback? onTap;
  final Widget? leading;

  @override
  Widget build(BuildContext context) {
    return StudyCard(
      onTap: onTap,
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      margin: const EdgeInsets.only(bottom: AppSpacing.xs),
      child: Row(
        children: [
          if (leading != null) ...[
            leading!,
            const SizedBox(width: AppSpacing.sm),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ),
          ),
          if (onTap != null)
            Icon(
              Icons.chevron_right,
              color: Theme.of(context).colorScheme.outline,
            ),
        ],
      ),
    );
  }
}
