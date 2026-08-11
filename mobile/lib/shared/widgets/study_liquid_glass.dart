import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';
import '../../core/theme/app_shadows.dart';
import '../../core/theme/app_spacing.dart';

enum LiquidGlassIntensity {
  soft(16),
  standard(28),
  strong(40);

  const LiquidGlassIntensity(this.blur);
  final double blur;
}

/// iPhone-style liquid glass — refraction fill, specular edge, deep blur.
///
/// Flutter Web backdrop blur is often weak; luminous multi-stop fills +
/// ambient blobs (`StudyGlassAtmosphere`) keep the surface reading as glass.
class StudyLiquidGlass extends StatelessWidget {
  const StudyLiquidGlass({
    super.key,
    required this.child,
    this.borderRadius,
    this.padding,
    this.margin,
    this.onTap,
    this.blur,
    this.tint,
    this.elevated = true,
    this.borderWidth = 1.25,
    this.intensity = LiquidGlassIntensity.standard,
  });

  final Widget child;
  final BorderRadius? borderRadius;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final VoidCallback? onTap;
  final double? blur;
  final Color? tint;
  final bool elevated;
  final double borderWidth;
  final LiquidGlassIntensity intensity;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final radius = borderRadius ?? AppRadius.surface;
    final webBoost = kIsWeb ? 1.4 : 1.0;
    final sigma = (blur ?? intensity.blur) * webBoost;

    final base = tint ??
        (dark ? AppColors.liquidGlassDark : AppColors.liquidGlassLight);
    final edge = dark
        ? AppColors.liquidGlassEdgeDark
        : AppColors.liquidGlassEdgeLight;
    final topSheen = dark
        ? Colors.white.withValues(alpha: 0.16)
        : Colors.white.withValues(alpha: 0.82);
    final midSheen = dark
        ? Colors.white.withValues(alpha: 0.05)
        : const Color(0x73FFFFFF);
    final bottomWash = dark
        ? Colors.black.withValues(alpha: 0.25)
        : AppColors.primary.withValues(alpha: 0.05);

    final content = Container(
      decoration: BoxDecoration(
        borderRadius: radius,
        boxShadow: elevated ? AppShadows.liquidDeep : null,
      ),
      child: ClipRRect(
        borderRadius: radius,
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
          child: DecoratedBox(
            decoration: BoxDecoration(
              borderRadius: radius,
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                stops: const [0.0, 0.32, 0.68, 1.0],
                colors: [
                  Color.alphaBlend(topSheen, base),
                  Color.alphaBlend(midSheen, base),
                  base,
                  Color.alphaBlend(bottomWash, base),
                ],
              ),
              border: Border.all(color: edge, width: borderWidth),
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onTap,
                borderRadius: radius,
                splashColor: AppColors.primary.withValues(alpha: 0.08),
                highlightColor: AppColors.primary.withValues(alpha: 0.04),
                child: Stack(
                  children: [
                    if (padding == null)
                      child
                    else
                      Padding(padding: padding!, child: child),
                    Positioned(
                      left: 8,
                      right: 8,
                      top: 1,
                      height: 1.25,
                      child: IgnorePointer(
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(99),
                            gradient: LinearGradient(
                              colors: [
                                Colors.white
                                    .withValues(alpha: dark ? 0.05 : 0.0),
                                Colors.white
                                    .withValues(alpha: dark ? 0.4 : 0.9),
                                Colors.white
                                    .withValues(alpha: dark ? 0.05 : 0.0),
                              ],
                            ),
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
      ),
    );

    if (margin == null) return content;
    return Padding(padding: margin!, child: content);
  }
}

/// Capsule liquid-glass chip used under CTAs / stats.
class StudyLiquidGlassCapsule extends StatelessWidget {
  const StudyLiquidGlassCapsule({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.symmetric(
      horizontal: AppSpacing.sm,
      vertical: AppSpacing.md,
    ),
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return StudyLiquidGlass(
      borderRadius: AppRadius.capsuleButton,
      padding: padding,
      onTap: onTap,
      intensity: LiquidGlassIntensity.strong,
      child: child,
    );
  }
}

/// Soft aurora / mesh backdrop so glass has something to refract (esp. web).
class StudyGlassAtmosphere extends StatelessWidget {
  const StudyGlassAtmosphere({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg = dark ? AppColors.backgroundDark : AppColors.background;

    return Stack(
      fit: StackFit.expand,
      children: [
        ColoredBox(color: bg),
        Positioned(
          top: -80,
          right: -40,
          child: _Blob(
            size: 220,
            color: (dark ? AppColors.primaryLight : AppColors.primary)
                .withValues(alpha: dark ? 0.22 : 0.12),
          ),
        ),
        Positioned(
          top: 180,
          left: -90,
          child: _Blob(
            size: 260,
            color: AppColors.info.withValues(alpha: dark ? 0.14 : 0.08),
          ),
        ),
        Positioned(
          bottom: 120,
          right: -60,
          child: _Blob(
            size: 200,
            color: AppColors.primaryLight.withValues(alpha: dark ? 0.16 : 0.10),
          ),
        ),
        child,
      ],
    );
  }
}

class _Blob extends StatelessWidget {
  const _Blob({required this.size, required this.color});

  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return ImageFiltered(
      imageFilter: ImageFilter.blur(sigmaX: 48, sigmaY: 48),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      ),
    );
  }
}
