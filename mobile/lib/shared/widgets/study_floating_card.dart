import 'package:flutter/material.dart';

import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';
import 'study_liquid_glass.dart';

/// Floating liquid-glass card for Home sections.
class StudyFloatingCard extends StatelessWidget {
  const StudyFloatingCard({
    super.key,
    required this.child,
    this.padding = AppSpacing.cardComfortable,
    this.margin,
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return StudyLiquidGlass(
      borderRadius: AppRadius.surface,
      padding: padding,
      margin: margin,
      onTap: onTap,
      child: child,
    );
  }
}
