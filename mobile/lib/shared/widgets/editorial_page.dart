import 'package:flutter/material.dart';

import '../../core/theme/app_spacing.dart';

/// Centers content with phone→tablet friendly max width and padding.
class EditorialPage extends StatelessWidget {
  const EditorialPage({
    super.key,
    required this.child,
    this.padding,
  });

  final Widget child;
  final EdgeInsetsGeometry? padding;

  static double maxContentWidth(double screenWidth) {
    if (screenWidth >= 1100) return 880;
    if (screenWidth >= 840) return 760;
    if (screenWidth >= 600) return 640;
    return 560;
  }

  static EdgeInsets horizontalPadding(double screenWidth) {
    if (screenWidth >= 840) {
      return const EdgeInsets.symmetric(horizontal: AppSpacing.xxl);
    }
    if (screenWidth >= 600) {
      return const EdgeInsets.symmetric(horizontal: AppSpacing.xl);
    }
    return const EdgeInsets.symmetric(horizontal: AppSpacing.md);
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final resolvedPadding = padding ??
        EdgeInsets.only(
          left: horizontalPadding(width).left,
          right: horizontalPadding(width).right,
          top: AppSpacing.xl,
          bottom: AppSpacing.xxl,
        );

    // Align (not Center) so scrollables keep viewport height.
    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: maxContentWidth(width),
          minHeight: MediaQuery.sizeOf(context).height,
        ),
        child: Padding(
          padding: resolvedPadding,
          child: child,
        ),
      ),
    );
  }
}
