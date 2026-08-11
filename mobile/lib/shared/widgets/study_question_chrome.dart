import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';
import '../../core/theme/app_spacing.dart';
import 'soft_progress.dart';
import 'study_glass_button.dart';

/// High-readability MCQ option — min ~52 touch height, tonal selected state.
class StudyChoiceOption extends StatelessWidget {
  const StudyChoiceOption({
    super.key,
    required this.letter,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String letter;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final text = Theme.of(context).textTheme;

    final bg = selected
        ? AppColors.primary.withValues(alpha: dark ? 0.22 : 0.10)
        : (dark ? AppColors.surfaceMutedDark : AppColors.surface);
    final border = selected
        ? AppColors.primary.withValues(alpha: 0.55)
        : (dark
            ? Colors.white.withValues(alpha: 0.08)
            : AppColors.divider.withValues(alpha: 0.9));

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: Material(
        color: bg,
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.surface,
          side: BorderSide(color: border, width: selected ? 1.5 : 1),
        ),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onTap,
          borderRadius: AppRadius.surface,
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 56),
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.sm,
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: selected
                          ? AppColors.primary
                          : AppColors.primary.withValues(alpha: 0.10),
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      letter,
                      style: text.labelLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: selected
                            ? AppColors.textOnPrimary
                            : AppColors.primary,
                      ),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        label,
                        style: text.bodyLarge?.copyWith(
                          height: 1.45,
                          fontSize: 16,
                          fontWeight:
                              selected ? FontWeight.w600 : FontWeight.w400,
                          color: dark
                              ? const Color(0xFFF8FAFC)
                              : AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Compact progress header for question sessions.
class StudyQuestionProgress extends StatelessWidget {
  const StudyQuestionProgress({
    super.key,
    required this.current,
    required this.total,
    this.subtitle,
    this.trailing,
  });

  final int current;
  final int total;
  final String? subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final progress = total <= 0 ? 0.0 : (current / total).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.md,
        AppSpacing.sm,
        AppSpacing.md,
        AppSpacing.xs,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  subtitle == null || subtitle!.isEmpty
                      ? '$current / $total'
                      : '$current / $total · $subtitle',
                  style: text.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.2,
                  ),
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          SoftProgress(value: progress, height: 5),
        ],
      ),
    );
  }
}

/// Footer: optional previous + glass next/finish.
class StudyQuestionFooter extends StatelessWidget {
  const StudyQuestionFooter({
    super.key,
    required this.canGoPrevious,
    required this.isLast,
    required this.submitting,
    required this.onPrevious,
    required this.onNext,
    required this.onSubmit,
  });

  final bool canGoPrevious;
  final bool isLast;
  final bool submitting;
  final VoidCallback onPrevious;
  final VoidCallback onNext;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          AppSpacing.md,
          AppSpacing.xs,
          AppSpacing.md,
          AppSpacing.md,
        ),
        child: Row(
          children: [
            if (canGoPrevious)
              StudyGlassButton(
                label: 'Önceki',
                leadingIcon: Icons.arrow_back_rounded,
                trailingIcon: null,
                showTrailing: false,
                variant: StudyGlassVariant.secondary,
                size: StudyGlassSize.medium,
                expand: false,
                onPressed: submitting ? null : onPrevious,
              ),
            if (canGoPrevious) const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: StudyGlassButton(
                label: isLast ? 'Bitir' : 'Sonraki Soru',
                leadingIcon: isLast
                    ? Icons.check_rounded
                    : Icons.play_arrow_rounded,
                loading: submitting && isLast,
                size: StudyGlassSize.large,
                onPressed: submitting && isLast
                    ? null
                    : (isLast ? onSubmit : onNext),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
