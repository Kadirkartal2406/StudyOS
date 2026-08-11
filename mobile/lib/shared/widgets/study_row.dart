import 'package:flutter/material.dart';

import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';

/// Settings / Apple Music style list row — no heavy card chrome.
class StudyRow extends StatelessWidget {
  const StudyRow({
    super.key,
    required this.title,
    this.subtitle,
    this.trailing,
    this.leading,
    this.leadingColor,
    this.onTap,
    this.showChevron = true,
    this.dense = false,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final IconData? leading;
  final Color? leadingColor;
  final VoidCallback? onTap;
  final bool showChevron;
  final bool dense;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;
    final accent = leadingColor ?? scheme.primary;
    final vPad = dense ? AppSpacing.sm : AppSpacing.md;

    final row = Padding(
      padding: EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: vPad,
      ),
      child: Row(
        children: [
          if (leading != null) ...[
            Container(
              width: 40,
              height: 40,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: accent.withValues(alpha: 0.12),
                borderRadius: AppRadius.chip,
              ),
              child: Icon(leading, size: 22, color: accent),
            ),
            const SizedBox(width: AppSpacing.sm),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: text.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.2,
                  ),
                ),
                if (subtitle != null && subtitle!.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(
                    subtitle!,
                    style: text.bodyMedium?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (trailing != null) ...[
            const SizedBox(width: AppSpacing.xs),
            trailing!,
          ],
          if (showChevron && onTap != null)
            Icon(
              Icons.chevron_right_rounded,
              color: scheme.onSurfaceVariant.withValues(alpha: 0.8),
            ),
        ],
      ),
    );

    if (onTap == null) return row;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: AppRadius.card,
        child: ConstrainedBox(
          constraints: const BoxConstraints(minHeight: 56),
          child: row,
        ),
      ),
    );
  }
}
