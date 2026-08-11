import 'dart:ui';

import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_radius.dart';
import '../../core/theme/app_shadows.dart';
import '../../core/theme/app_spacing.dart';
import 'study_icons.dart';

/// Visual role for Glass / Floating actions (D — reference).
enum StudyGlassVariant {
  primary,
  secondary,
  success,
  info,
  warning,
  danger,
}

enum StudyGlassSize {
  large,
  medium,
  small,
}

/// Capsule liquid-glass CTA — icon · label · trailing.
///
/// States: default · pressed · disabled · loading.
/// Does not change navigation or business logic — presentation only.
class StudyGlassButton extends StatefulWidget {
  const StudyGlassButton({
    super.key,
    required this.label,
    this.onPressed,
    this.leadingIcon = StudyIcons.play,
    this.trailingIcon = StudyIcons.next,
    this.variant = StudyGlassVariant.primary,
    this.size = StudyGlassSize.medium,
    this.expand = true,
    this.loading = false,
    this.showTrailing = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final IconData? leadingIcon;
  final IconData? trailingIcon;
  final StudyGlassVariant variant;
  final StudyGlassSize size;
  final bool expand;
  final bool loading;
  final bool showTrailing;

  @override
  State<StudyGlassButton> createState() => _StudyGlassButtonState();
}

class _StudyGlassButtonState extends State<StudyGlassButton> {
  bool _pressed = false;

  bool get _enabled => widget.onPressed != null && !widget.loading;

  double get _height => switch (widget.size) {
        StudyGlassSize.large => 56,
        StudyGlassSize.medium => 48,
        StudyGlassSize.small => 40,
      };

  double get _iconBox => switch (widget.size) {
        StudyGlassSize.large => 36,
        StudyGlassSize.medium => 32,
        StudyGlassSize.small => 28,
      };

  double get _fontSize => switch (widget.size) {
        StudyGlassSize.large => 16,
        StudyGlassSize.medium => 15,
        StudyGlassSize.small => 14,
      };

  _GlassPalette _palette(Brightness brightness) {
    final dark = brightness == Brightness.dark;
    return switch (widget.variant) {
      StudyGlassVariant.primary => _GlassPalette(
          fill: dark ? AppColors.liquidGlassDark : AppColors.liquidGlassLight,
          border: dark
              ? AppColors.liquidGlassEdgeDark
              : AppColors.primarySoftBorder,
          foreground: AppColors.onSurfaceOf(brightness),
          accent: AppColors.primary,
          accentOn: AppColors.textOnPrimary,
          pressedFill: AppColors.primary,
          pressedForeground: AppColors.textOnPrimary,
          elevated: true,
        ),
      StudyGlassVariant.secondary => _GlassPalette.tonal(
          accent: AppColors.primary,
          soft: AppColors.primarySoft,
          dark: dark,
        ),
      StudyGlassVariant.success => _GlassPalette.tonal(
          accent: AppColors.success,
          soft: AppColors.successSoft,
          dark: dark,
        ),
      StudyGlassVariant.info => _GlassPalette.tonal(
          accent: AppColors.info,
          soft: AppColors.infoSoft,
          dark: dark,
        ),
      StudyGlassVariant.warning => _GlassPalette.tonal(
          accent: AppColors.warning,
          soft: AppColors.warningSoft,
          dark: dark,
        ),
      StudyGlassVariant.danger => _GlassPalette.tonal(
          accent: AppColors.danger,
          soft: AppColors.errorSoft,
          dark: dark,
        ),
    };
  }

  @override
  Widget build(BuildContext context) {
    final brightness = Theme.of(context).brightness;
    final palette = _palette(brightness);
    final pressed = _pressed && _enabled;
    final disabled = !_enabled && !widget.loading;

    final bg = pressed ? palette.pressedFill : palette.fill;
    final fg = pressed ? palette.pressedForeground : palette.foreground;
    final border = pressed ? Colors.transparent : palette.border;

    final resolvedBg = disabled ? _fade(bg, 0.5) : bg;
    final resolvedBorder = disabled ? _fade(border, 0.35) : border;
    final resolvedFg = disabled ? _fade(fg, 0.55) : fg;

    final shadows = disabled || !palette.elevated || pressed
        ? const <BoxShadow>[]
        : AppShadows.liquid;

    final inner = SizedBox(
      height: _height,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm),
        child: Row(
          mainAxisSize: widget.expand ? MainAxisSize.max : MainAxisSize.min,
          children: [
            _LeadingSlot(
              loading: widget.loading,
              icon: widget.leadingIcon,
              size: _iconBox,
              accent: palette.accent,
              pressed: pressed,
            ),
            const SizedBox(width: AppSpacing.sm),
            if (widget.expand)
              Expanded(
                child: Text(
                  widget.loading ? 'Yükleniyor...' : widget.label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: _fontSize,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.1,
                    color: resolvedFg,
                  ),
                ),
              )
            else
              Text(
                widget.loading ? 'Yükleniyor...' : widget.label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: _fontSize,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.1,
                  color: resolvedFg,
                ),
              ),
            if (widget.showTrailing && widget.trailingIcon != null) ...[
              const SizedBox(width: AppSpacing.xs),
              Icon(
                widget.trailingIcon,
                size: 18,
                color: resolvedFg.withValues(alpha: disabled ? 0.35 : 0.72),
              ),
              const SizedBox(width: AppSpacing.xs),
            ],
          ],
        ),
      ),
    );

    final glass = AnimatedContainer(
      duration: const Duration(milliseconds: 140),
      curve: Curves.easeOutCubic,
      decoration: BoxDecoration(
        borderRadius: AppRadius.capsuleButton,
        boxShadow: shadows,
      ),
      child: ClipRRect(
        borderRadius: AppRadius.capsuleButton,
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: pressed ? 8 : 20, sigmaY: pressed ? 8 : 20),
          child: DecoratedBox(
            decoration: BoxDecoration(
              borderRadius: AppRadius.capsuleButton,
              gradient: pressed
                  ? null
                  : LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color.alphaBlend(
                          Colors.white.withValues(
                            alpha: brightness == Brightness.dark ? 0.08 : 0.45,
                          ),
                          resolvedBg,
                        ),
                        resolvedBg,
                      ],
                    ),
              color: pressed ? resolvedBg : null,
              border: Border.all(color: resolvedBorder, width: 1),
            ),
            child: inner,
          ),
        ),
      ),
    );

    final button = Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: _enabled ? widget.onPressed : null,
        onHighlightChanged: (v) {
          if (!_enabled) return;
          setState(() => _pressed = v);
        },
        borderRadius: AppRadius.capsuleButton,
        splashColor: palette.accent.withValues(alpha: 0.08),
        highlightColor: Colors.transparent,
        child: glass,
      ),
    );

    if (!widget.expand) return button;
    return SizedBox(width: double.infinity, child: button);
  }

  static Color _fade(Color color, double factor) {
    return color.withValues(alpha: (color.a * factor).clamp(0.0, 1.0));
  }
}

class _LeadingSlot extends StatelessWidget {
  const _LeadingSlot({
    required this.loading,
    required this.icon,
    required this.size,
    required this.accent,
    required this.pressed,
  });

  final bool loading;
  final IconData? icon;
  final double size;
  final Color accent;
  final bool pressed;

  @override
  Widget build(BuildContext context) {
    final circleColor =
        pressed ? Colors.white.withValues(alpha: 0.22) : accent;
    const iconColor = AppColors.textOnPrimary;

    return Container(
      width: size,
      height: size,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: circleColor,
        shape: BoxShape.circle,
        boxShadow: pressed
            ? null
            : [
                BoxShadow(
                  color: accent.withValues(alpha: 0.28),
                  blurRadius: 10,
                  offset: const Offset(0, 3),
                ),
              ],
      ),
      child: loading
          ? SizedBox(
              width: size * 0.45,
              height: size * 0.45,
              child: const CircularProgressIndicator(
                strokeWidth: 2,
                color: iconColor,
              ),
            )
          : (icon == null
              ? const SizedBox.shrink()
              : Icon(icon, size: size * 0.55, color: iconColor)),
    );
  }
}

class _GlassPalette {
  const _GlassPalette({
    required this.fill,
    required this.border,
    required this.foreground,
    required this.accent,
    required this.accentOn,
    required this.pressedFill,
    required this.pressedForeground,
    required this.elevated,
  });

  factory _GlassPalette.tonal({
    required Color accent,
    required Color soft,
    required bool dark,
  }) {
    final glassBase =
        dark ? AppColors.liquidGlassDark : AppColors.liquidGlassLight;
    return _GlassPalette(
      fill: Color.alphaBlend(soft, glassBase),
      border: dark
          ? AppColors.liquidGlassEdgeDark
          : accent.withValues(alpha: 0.22),
      foreground: AppColors.onSurfaceOf(
        dark ? Brightness.dark : Brightness.light,
      ),
      accent: accent,
      accentOn: AppColors.textOnPrimary,
      pressedFill: accent,
      pressedForeground: AppColors.textOnPrimary,
      elevated: true,
    );
  }

  final Color fill;
  final Color border;
  final Color foreground;
  final Color accent;
  final Color accentOn;
  final Color pressedFill;
  final Color pressedForeground;
  final bool elevated;
}

/// Circular liquid-glass icon control — min 44×44 touch target.
class StudyIconButton extends StatefulWidget {
  const StudyIconButton({
    super.key,
    required this.icon,
    this.onPressed,
    this.tooltip,
    this.variant = StudyGlassVariant.secondary,
    this.size = 44,
  });

  final IconData icon;
  final VoidCallback? onPressed;
  final String? tooltip;
  final StudyGlassVariant variant;
  final double size;

  @override
  State<StudyIconButton> createState() => _StudyIconButtonState();
}

class _StudyIconButtonState extends State<StudyIconButton> {
  bool _pressed = false;

  bool get _enabled => widget.onPressed != null;

  Color _accent() => switch (widget.variant) {
        StudyGlassVariant.primary || StudyGlassVariant.secondary =>
          AppColors.primary,
        StudyGlassVariant.success => AppColors.success,
        StudyGlassVariant.info => AppColors.info,
        StudyGlassVariant.warning => AppColors.warning,
        StudyGlassVariant.danger => AppColors.danger,
      };

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final accent = _accent();
    final pressed = _pressed && _enabled;
    final side = widget.size < 44 ? 44.0 : widget.size;
    final fill = dark ? AppColors.liquidGlassDark : AppColors.liquidGlassLight;

    final box = ClipOval(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 140),
          width: side,
          height: side,
          decoration: BoxDecoration(
            color: pressed ? accent : fill,
            shape: BoxShape.circle,
            border: Border.all(
              color: pressed
                  ? Colors.transparent
                  : (dark
                      ? AppColors.liquidGlassEdgeDark
                      : accent.withValues(alpha: 0.22)),
            ),
            boxShadow: _enabled && !pressed ? AppShadows.floatingPressed : null,
          ),
          child: Icon(
            widget.icon,
            size: side * 0.45,
            color: pressed
                ? AppColors.textOnPrimary
                : accent.withValues(alpha: _enabled ? 1 : 0.4),
          ),
        ),
      ),
    );

    final button = Material(
      color: Colors.transparent,
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: widget.onPressed,
        onHighlightChanged: (v) {
          if (!_enabled) return;
          setState(() => _pressed = v);
        },
        child: box,
      ),
    );

    if (widget.tooltip == null) return button;
    return Tooltip(message: widget.tooltip!, child: button);
  }
}
