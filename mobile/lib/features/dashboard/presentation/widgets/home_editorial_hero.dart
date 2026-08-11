import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_radius.dart';
import '../../../../core/theme/app_spacing.dart';

/// Home editorial hero — display typography + one calm study photo.
class HomeEditorialHero extends StatelessWidget {
  const HomeEditorialHero({
    super.key,
    required this.greeting,
    required this.headline,
    this.supporting,
    this.examLine,
    this.imageAsset = 'assets/images/home_study_hero.png',
  });

  final String greeting;
  final String headline;
  final String? supporting;
  final String? examLine;
  final String imageAsset;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    // Prefer stacked hero on typical phone widths; side-by-side on tablet+.
    final wide = width >= 840;
    final textBlock = _TextBlock(
      greeting: greeting,
      headline: headline,
      supporting: supporting,
      examLine: examLine,
    );
    final image = _HeroImage(asset: imageAsset, tall: wide);

    if (wide) {
      return Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(flex: 5, child: textBlock),
          const SizedBox(width: AppSpacing.xl),
          Expanded(flex: 4, child: image),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        textBlock,
        const SizedBox(height: AppSpacing.lg),
        image,
      ],
    );
  }
}

class _TextBlock extends StatelessWidget {
  const _TextBlock({
    required this.greeting,
    required this.headline,
    this.supporting,
    this.examLine,
  });

  final String greeting;
  final String headline;
  final String? supporting;
  final String? examLine;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          greeting,
          style: text.titleMedium?.copyWith(
            color: scheme.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          headline,
          style: text.displaySmall?.copyWith(
            fontWeight: FontWeight.w700,
            height: 1.15,
            letterSpacing: -0.6,
          ),
        ),
        if (examLine != null && examLine!.isNotEmpty) ...[
          const SizedBox(height: AppSpacing.sm),
          Text(
            examLine!,
            style: text.titleSmall?.copyWith(
              color: scheme.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
        if (supporting != null && supporting!.trim().isNotEmpty) ...[
          const SizedBox(height: AppSpacing.md),
          Text(
            supporting!.trim(),
            style: text.bodyLarge?.copyWith(
              color: scheme.onSurfaceVariant,
              height: 1.45,
            ),
          ),
        ],
      ],
    );
  }
}

class _HeroImage extends StatelessWidget {
  const _HeroImage({required this.asset, required this.tall});

  final String asset;
  final bool tall;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return ClipRRect(
      borderRadius: AppRadius.heroImage,
      child: AspectRatio(
        aspectRatio: tall ? 4 / 5 : 16 / 10,
        child: Stack(
          fit: StackFit.expand,
          children: [
            Image.asset(
              asset,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => Container(
                color: AppColors.surfaceTonal,
                alignment: Alignment.center,
                child: Icon(
                  Icons.menu_book_rounded,
                  size: 48,
                  color: Theme.of(context).colorScheme.primary,
                ),
              ),
            ),
            // Soft readable wash — not heavy blur.
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: isDark ? 0.18 : 0.04),
                    Colors.black.withValues(alpha: isDark ? 0.28 : 0.10),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
