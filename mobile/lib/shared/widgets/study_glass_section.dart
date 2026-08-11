import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';
import 'study_floating_card.dart';
import 'study_row.dart';

/// Grouped liquid-glass menu / settings section.
class StudyGlassSection extends StatelessWidget {
  const StudyGlassSection({
    super.key,
    required this.title,
    required this.children,
    this.trailing,
  });

  final String title;
  final List<Widget> children;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.only(
            left: AppSpacing.xxs,
            bottom: AppSpacing.sm,
            right: AppSpacing.xxs,
          ),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: text.labelLarge?.copyWith(
                    color: scheme.onSurfaceVariant,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.3,
                  ),
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
        ),
        StudyFloatingCard(
          padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
          child: Column(children: children),
        ),
      ],
    );
  }
}

/// Menu row with StudyOS outlined icon + chevron.
class StudyMenuTile extends StatelessWidget {
  const StudyMenuTile({
    super.key,
    required this.title,
    required this.icon,
    required this.onTap,
    this.subtitle,
    this.iconColor,
    this.danger = false,
  });

  final String title;
  final String? subtitle;
  final IconData icon;
  final Color? iconColor;
  final VoidCallback onTap;
  final bool danger;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final accent = danger
        ? scheme.error
        : (iconColor ?? scheme.primary);

    return StudyRow(
      title: title,
      subtitle: subtitle,
      leading: icon,
      leadingColor: accent,
      showChevron: true,
      onTap: onTap,
    );
  }
}
