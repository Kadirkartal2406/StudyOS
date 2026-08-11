import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';
import 'app_radius.dart';
import 'app_spacing.dart';

/// StudyOS uygulama teması — editorial typography, quiet surfaces.
class AppTheme {
  AppTheme._();

  static TextTheme _textTheme(Color color) {
    final base = GoogleFonts.plusJakartaSansTextTheme();
    TextStyle style(
      TextStyle? s, {
      FontWeight? weight,
      double? size,
      double? spacing,
      double? height,
    }) {
      return (s ?? const TextStyle()).copyWith(
        color: color,
        fontWeight: weight,
        fontSize: size,
        letterSpacing: spacing,
        height: height ?? 1.35,
      );
    }

    return base.copyWith(
      displayLarge:
          style(base.displayLarge, weight: FontWeight.w700, size: 40, spacing: -0.8),
      displayMedium:
          style(base.displayMedium, weight: FontWeight.w700, size: 34, spacing: -0.6),
      displaySmall:
          style(base.displaySmall, weight: FontWeight.w700, size: 28, spacing: -0.4),
      headlineLarge:
          style(base.headlineLarge, weight: FontWeight.w700, size: 26, spacing: -0.3),
      headlineMedium:
          style(base.headlineMedium, weight: FontWeight.w700, size: 22, spacing: -0.2),
      headlineSmall:
          style(base.headlineSmall, weight: FontWeight.w600, size: 20),
      titleLarge: style(base.titleLarge, weight: FontWeight.w600, size: 18),
      titleMedium:
          style(base.titleMedium, weight: FontWeight.w600, size: 16, spacing: 0.1),
      titleSmall:
          style(base.titleSmall, weight: FontWeight.w600, size: 14, spacing: 0.1),
      bodyLarge: style(base.bodyLarge, weight: FontWeight.w400, size: 16, height: 1.45),
      bodyMedium:
          style(base.bodyMedium, weight: FontWeight.w400, size: 15, height: 1.45),
      bodySmall: style(base.bodySmall, weight: FontWeight.w400, size: 13, height: 1.4),
      labelLarge:
          style(base.labelLarge, weight: FontWeight.w600, size: 14, spacing: 0.15),
      labelMedium:
          style(base.labelMedium, weight: FontWeight.w600, size: 12, spacing: 0.2),
      labelSmall:
          style(base.labelSmall, weight: FontWeight.w600, size: 12, spacing: 0.2),
    );
  }

  static bool _isBrandAccent(Color? seed) =>
      seed == null || seed.toARGB32() == AppColors.primary.toARGB32();

  static ColorScheme _lightScheme() => const ColorScheme(
        brightness: Brightness.light,
        primary: AppColors.primary,
        onPrimary: AppColors.textOnPrimary,
        primaryContainer: Color(0xFFCCFBF1),
        onPrimaryContainer: AppColors.primaryDark,
        secondary: AppColors.secondary,
        onSecondary: Colors.white,
        secondaryContainer: Color(0xFFE2E8F0),
        onSecondaryContainer: AppColors.secondary,
        tertiary: AppColors.accent,
        onTertiary: Colors.white,
        error: AppColors.error,
        onError: Colors.white,
        surface: AppColors.surface,
        onSurface: AppColors.textPrimary,
        onSurfaceVariant: AppColors.textSecondary,
        outline: AppColors.outline,
        outlineVariant: AppColors.divider,
        surfaceContainerHighest: AppColors.surfaceMuted,
      );

  static ColorScheme _darkScheme() => const ColorScheme(
        brightness: Brightness.dark,
        primary: Color(0xFF2DD4BF),
        onPrimary: Color(0xFF042F2E),
        primaryContainer: Color(0xFF134E4A),
        onPrimaryContainer: Color(0xFFCCFBF1),
        secondary: Color(0xFF94A3B8),
        onSecondary: Color(0xFF0F172A),
        secondaryContainer: AppColors.surfaceMutedDark,
        onSecondaryContainer: Color(0xFFE2E8F0),
        tertiary: Color(0xFF38BDF8),
        onTertiary: Color(0xFF0C4A6E),
        error: Color(0xFFF87171),
        onError: Color(0xFF450A0A),
        surface: AppColors.surfaceDark,
        onSurface: Color(0xFFF8FAFC),
        onSurfaceVariant: Color(0xFF94A3B8),
        outline: Color(0xFF64748B),
        outlineVariant: Color(0xFF334155),
        surfaceContainerHighest: AppColors.surfaceMutedDark,
      );

  /// Keep handcrafted surfaces; only tint primary when user picks a custom accent.
  static ColorScheme _withAccent(ColorScheme base, Color? seed) {
    if (_isBrandAccent(seed)) return base;
    final accent = seed!;
    return base.copyWith(
      primary: accent,
      primaryContainer: Color.lerp(accent, Colors.white, 0.82)!,
      onPrimaryContainer: Color.lerp(accent, Colors.black, 0.55)!,
    );
  }

  static ThemeData lightTheme({Color? seed}) {
    return _base(_withAccent(_lightScheme(), seed), AppColors.background);
  }

  static ThemeData darkTheme({Color? seed}) {
    return _base(
      _withAccent(_darkScheme(), seed),
      AppColors.backgroundDark,
    );
  }

  static ThemeData _base(ColorScheme colorScheme, Color scaffoldBg) {
    final text = _textTheme(colorScheme.onSurface);
    final buttonShape = RoundedRectangleBorder(borderRadius: AppRadius.button);
    final isDark = colorScheme.brightness == Brightness.dark;

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: scaffoldBg,
      textTheme: text,
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: scaffoldBg,
        foregroundColor: colorScheme.onSurface,
        titleTextStyle: text.titleLarge,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(48, 52),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 14),
          shape: buttonShape,
          textStyle: text.labelLarge,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(48, 52),
          padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 14),
          shape: buttonShape,
          textStyle: text.labelLarge,
          elevation: 0,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: buttonShape,
          side: BorderSide(
            color: colorScheme.outlineVariant.withValues(alpha: 0.7),
          ),
          textStyle: text.labelLarge,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: const Size(48, 40),
          textStyle: text.labelLarge,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colorScheme.surface,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        border: OutlineInputBorder(
          borderRadius: AppRadius.card,
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.card,
          borderSide: BorderSide(
            color: colorScheme.outlineVariant.withValues(alpha: 0.65),
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: AppRadius.card,
          borderSide: BorderSide(color: colorScheme.primary, width: 1.5),
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: isDark ? colorScheme.surface : AppColors.surface,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.surface,
          side: BorderSide.none,
        ),
        clipBehavior: Clip.antiAlias,
        shadowColor: Colors.transparent,
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: AppRadius.chip),
        side: BorderSide.none,
        backgroundColor: isDark
            ? AppColors.surfaceMutedDark
            : AppColors.surfaceMuted,
        labelStyle: text.labelMedium,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      ),
      dividerTheme: DividerThemeData(
        color: colorScheme.outlineVariant.withValues(alpha: 0.55),
        thickness: 1,
        space: AppSpacing.lg,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: colorScheme.surface.withValues(alpha: 0.92),
        elevation: 0,
        shadowColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        indicatorColor: colorScheme.primaryContainer.withValues(alpha: 0.85),
        labelTextStyle: WidgetStatePropertyAll(text.labelSmall),
        height: 70,
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: colorScheme.surface,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.sheet),
        showDragHandle: true,
        elevation: 0,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: colorScheme.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.surface),
      ),
      pageTransitionsTheme: const PageTransitionsTheme(
        builders: {
          TargetPlatform.android: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
          TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.macOS: FadeUpwardsPageTransitionsBuilder(),
          TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
        },
      ),
    );
  }
}
