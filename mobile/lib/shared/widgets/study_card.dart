import 'package:flutter/material.dart';

import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';

/// Standard surface — borderless by default; optional hairline when needed.
class StudyCard extends StatelessWidget {
  const StudyCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding = AppSpacing.card,
    this.color,
    this.borderColor,
    this.margin,
    this.bordered = false,
  });

  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry padding;
  final Color? color;
  final Color? borderColor;
  final EdgeInsetsGeometry? margin;
  final bool bordered;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final card = Material(
      color: color ?? scheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: AppRadius.surface,
        side: bordered
            ? BorderSide(
                color: borderColor ??
                    scheme.outlineVariant.withValues(alpha: 0.55),
              )
            : BorderSide.none,
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Padding(padding: padding, child: child),
      ),
    );
    if (margin == null) return card;
    return Padding(padding: margin!, child: card);
  }
}
