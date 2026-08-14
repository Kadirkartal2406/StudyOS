import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_radius.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_floating_card.dart';
import '../../../../shared/widgets/study_glass_button.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Testler home section — liquid glass + StudyOS icons.
class HomeTestlerCard extends StatelessWidget {
  const HomeTestlerCard({super.key, required this.dashboard});

  final DashboardEntity dashboard;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final exam = (dashboard.activeExamType ?? dashboard.primaryExamType ?? '')
        .toUpperCase();

    final items = <_TestItem>[
      const _TestItem(
        title: 'Günün Denemesi',
        subtitle: 'Her gün yenilenir · tam deneme',
        icon: StudyIcons.exam,
        color: AppColors.info,
        route: '/assessment/daily',
      ),
    ];

    if (dashboard.lastExamTitle != null &&
        dashboard.lastExamTitle!.trim().isNotEmpty) {
      final net = dashboard.lastExamNet;
      items.add(
        _TestItem(
          title: dashboard.lastExamTitle!,
          subtitle: net != null
              ? 'Son deneme · Net ${net.toStringAsFixed(1)}'
              : 'Son deneme',
          icon: StudyIcons.quiz,
          color: AppColors.primary,
          route: '/assessment',
        ),
      );
    } else if (exam.isNotEmpty) {
      items.add(
        _TestItem(
          title: '$exam Deneme',
          subtitle: dashboard.assessmentMessage ?? 'Deneme çözmeye başla',
          icon: StudyIcons.document,
          color: AppColors.primaryLight,
          route: '/assessment',
        ),
      );
    }

    if (dashboard.revisionDueToday > 0) {
      items.add(
        _TestItem(
          title: dashboard.revisionNextTitle ?? 'Tekrar Testi',
          subtitle: 'Bugün ${dashboard.revisionDueToday} tekrar bekliyor',
          icon: StudyIcons.revision,
          color: AppColors.warning,
          route: '/revisions',
        ),
      );
    }

    final visible = items.take(3).toList();

    return StudyFloatingCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Testler',
                  style: text.titleLarge?.copyWith(
                    color: scheme.onSurface,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.3,
                  ),
                ),
              ),
              TextButton(
                onPressed: () => context.push('/assessment'),
                style: TextButton.styleFrom(
                  foregroundColor: scheme.primary,
                  padding: EdgeInsets.zero,
                  minimumSize: const Size(44, 44),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: const Text('Tümü'),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          for (var i = 0; i < visible.length; i++) ...[
            if (i > 0) const SizedBox(height: AppSpacing.xs),
            _TestRow(item: visible[i]),
          ],
          const SizedBox(height: AppSpacing.md),
          StudyGlassButton(
            label: 'Teste Başla',
            leadingIcon: StudyIcons.document,
            variant: StudyGlassVariant.info,
            size: StudyGlassSize.medium,
            onPressed: () => context.push('/assessment/daily'),
          ),
        ],
      ),
    );
  }
}

class _TestItem {
  const _TestItem({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.route,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final String route;
}

class _TestRow extends StatelessWidget {
  const _TestRow({required this.item});

  final _TestItem item;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return InkWell(
      borderRadius: AppRadius.chip,
      onTap: () => context.push(item.route),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: item.color.withValues(alpha: 0.14),
                borderRadius: AppRadius.chip,
              ),
              child: Icon(item.icon, size: 22, color: item.color),
            ),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: text.titleMedium?.copyWith(
                      color: scheme.onSurface,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    item.subtitle,
                    style: text.bodyMedium?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              StudyIcons.next,
              color: scheme.onSurfaceVariant,
            ),
          ],
        ),
      ),
    );
  }
}
