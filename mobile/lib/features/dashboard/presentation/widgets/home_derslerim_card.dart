import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_radius.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_floating_card.dart';
import '../../../../shared/widgets/study_glass_button.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Derslerim home section — liquid glass + StudyOS icons.
class HomeDerslerimCard extends StatelessWidget {
  const HomeDerslerimCard({
    super.key,
    required this.dashboard,
    this.onContinue,
  });

  final DashboardEntity dashboard;
  final VoidCallback? onContinue;

  static const _palette = <Color>[
    AppColors.info,
    AppColors.success,
    AppColors.warning,
    AppColors.primary,
    AppColors.primaryLight,
  ];

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final names = dashboard.mySubjectNames;
    final codes = dashboard.mySubjectCodes;
    final progress = dashboard.dailyProgressPercentage.round().clamp(0, 100);
    final topicHint = dashboard.todayStudiedTopic ??
        dashboard.nextAction?.subtitle ??
        dashboard.subjectsMostStudied;

    final items = <_SubjectItem>[];
    for (var i = 0; i < names.length && i < 3; i++) {
      final code = i < codes.length ? codes[i] : null;
      items.add(
        _SubjectItem(
          name: names[i],
          code: code,
          topic: i == 0 && topicHint != null && topicHint.isNotEmpty
              ? topicHint
              : (dashboard.nextAction?.subjectCode == code
                  ? (dashboard.nextAction?.title ?? 'Devam et')
                  : 'Konuya devam'),
          percent: i == 0
              ? progress
              : ((progress - (i * 12)).clamp(8, 100)).toInt(),
          color: _palette[i % _palette.length],
          icon: StudyIcons.subjectGlyphs[i % StudyIcons.subjectGlyphs.length],
        ),
      );
    }

    if (items.isEmpty) {
      items.add(
        _SubjectItem(
          name: dashboard.mostStudiedSubject ?? 'Derslerim',
          code: dashboard.nextAction?.subjectCode,
          topic: topicHint ?? 'Bugün çalışmaya başla',
          percent: progress,
          color: _palette.first,
          icon: StudyIcons.subjects,
        ),
      );
    }

    return StudyFloatingCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Derslerim',
                  style: text.titleLarge?.copyWith(
                    color: scheme.onSurface,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.3,
                  ),
                ),
              ),
              TextButton(
                onPressed: () => context.go('/subjects'),
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
          for (var i = 0; i < items.length; i++) ...[
            if (i > 0) const SizedBox(height: AppSpacing.xs),
            _SubjectRow(item: items[i]),
          ],
          const SizedBox(height: AppSpacing.md),
          StudyGlassButton(
            label: 'Derse Devam Et',
            leadingIcon: StudyIcons.bookmark,
            variant: StudyGlassVariant.secondary,
            size: StudyGlassSize.medium,
            onPressed: onContinue ??
                () {
                  final link = dashboard.nextAction?.deepLinkHint;
                  if (link != null && link.isNotEmpty) {
                    context.push(link);
                  } else {
                    context.go('/subjects');
                  }
                },
          ),
        ],
      ),
    );
  }
}

class _SubjectItem {
  const _SubjectItem({
    required this.name,
    required this.topic,
    required this.percent,
    required this.color,
    required this.icon,
    this.code,
  });

  final String name;
  final String? code;
  final String topic;
  final int percent;
  final Color color;
  final IconData icon;
}

class _SubjectRow extends StatelessWidget {
  const _SubjectRow({required this.item});

  final _SubjectItem item;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return InkWell(
      borderRadius: AppRadius.chip,
      onTap: item.code != null && item.code!.isNotEmpty
          ? () => context.push('/subjects/${item.code}')
          : () => context.go('/subjects'),
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
                    item.name,
                    style: text.titleMedium?.copyWith(
                      color: scheme.onSurface,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    item.topic,
                    style: text.bodyMedium?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              '%${item.percent}',
              style: text.titleSmall?.copyWith(
                color: scheme.primary,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
