import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';

/// Borderless tonal surface — preferred over bordered cards in editorial UI.
class StudySurface extends StatelessWidget {
  const StudySurface({
    super.key,
    required this.child,
    this.onTap,
    this.padding = AppSpacing.cardComfortable,
    this.color,
    this.borderRadius,
    this.margin,
  });

  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry padding;
  final Color? color;
  final BorderRadius? borderRadius;
  final EdgeInsetsGeometry? margin;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isDark = scheme.brightness == Brightness.dark;
    final bg = color ??
        (isDark ? AppColors.surfaceTonalDark : AppColors.surfaceTonal);
    final radius = borderRadius ?? AppRadius.surface;

    final surface = Material(
      color: bg,
      shape: RoundedRectangleBorder(borderRadius: radius),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        borderRadius: radius,
        child: Padding(padding: padding, child: child),
      ),
    );

    if (margin == null) return surface;
    return Padding(padding: margin!, child: surface);
  }
}
