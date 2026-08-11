import 'package:flutter/material.dart';

import '../../core/theme/app_radius.dart';

/// Thin, calm progress bar for goals and session feedback.
class SoftProgress extends StatelessWidget {
  const SoftProgress({
    super.key,
    required this.value,
    this.height = 6,
    this.color,
    this.backgroundColor,
  });

  /// 0–1
  final double value;
  final double height;
  final Color? color;
  final Color? backgroundColor;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final clamped = value.clamp(0.0, 1.0);
    return ClipRRect(
      borderRadius: BorderRadius.circular(AppRadius.sm),
      child: LinearProgressIndicator(
        value: clamped,
        minHeight: height,
        backgroundColor:
            backgroundColor ?? scheme.primary.withValues(alpha: 0.12),
        color: color ?? scheme.primary,
      ),
    );
  }
}
