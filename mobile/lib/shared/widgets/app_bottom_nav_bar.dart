import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';
import 'study_icons.dart';
import 'study_liquid_glass.dart';

/// Alt gezinme — 5 tab; liquid glass + StudyOS icon system.
class AppBottomNavBar extends StatelessWidget {
  const AppBottomNavBar({super.key, required this.currentIndex});

  final int currentIndex;

  static const _destinations = [
    (icon: StudyIcons.today, label: 'Bugün', route: '/dashboard'),
    (icon: StudyIcons.subjects, label: 'Derslerim', route: '/subjects'),
    (icon: StudyIcons.focus, label: 'Odak', route: '/pomodoro'),
    (icon: StudyIcons.plan, label: 'Planım', route: '/study-plan'),
    (icon: StudyIcons.menu, label: 'Menü', route: '/menu'),
  ];

  void _handleTap(BuildContext context, int index) {
    if (index == currentIndex) return;
    context.go(_destinations[index].route);
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          AppSpacing.md,
          0,
          AppSpacing.md,
          AppSpacing.sm,
        ),
        child: StudyLiquidGlass(
          borderRadius: AppRadius.surface,
          blur: 26,
          child: SizedBox(
            height: 68,
            child: Row(
              children: [
                for (var i = 0; i < _destinations.length; i++)
                  Expanded(
                    child: _NavItem(
                      icon: _destinations[i].icon,
                      label: _destinations[i].label,
                      selected: i == currentIndex,
                      onTap: () => _handleTap(context, i),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.icon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final color = selected
        ? (dark ? const Color(0xFF2DD4BF) : AppColors.primary)
        : AppColors.onSurfaceVariantOf(Theme.of(context).brightness)
            .withValues(alpha: 0.9);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: AppRadius.card,
        child: Semantics(
          button: true,
          selected: selected,
          label: label,
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 44, minWidth: 44),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 160),
                  curve: Curves.easeOutCubic,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: selected
                        ? AppColors.primary.withValues(alpha: dark ? 0.22 : 0.12)
                        : Colors.transparent,
                    borderRadius: AppRadius.chip,
                  ),
                  child: Icon(icon, size: 22, color: color),
                ),
                const SizedBox(height: 2),
                Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                    color: color,
                    letterSpacing: 0.1,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
