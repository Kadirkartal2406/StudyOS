import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';
import 'app_radius.dart';
import 'app_spacing.dart';

/// Sprint 16 — StudyOS uygulama teması (token-driven).
class AppTheme {
  AppTheme._();

  static TextTheme _textTheme(Color color) {
    final base = GoogleFonts.plusJakartaSansTextTheme();
    TextStyle style(TextStyle? s, {FontWeight? weight, double? size, double? spacing}) {
      return (s ?? const TextStyle()).copyWith(
        color: color,
        fontWeight: weight,
        fontSize: size,
        letterSpacing: spacing,
        height: 1.35,
      );
    }

    return base.copyWith(
      displayLarge: style(base.displayLarge, weight: FontWeight.w700, size: 40, spacing: -0.5),
      displayMedium: style(base.displayMedium, weight: FontWeight.w700, size: 32, spacing: -0.3),
      displaySmall: style(base.displaySmall, weight: FontWeight.w700, size: 28),
      headlineLarge: style(base.headlineLarge, weight: FontWeight.w700, size: 26),
      headlineMedium: style(base.headlineMedium, weight: FontWeight.w700, size: 22),
      headlineSmall: style(base.headlineSmall, weight: FontWeight.w600, size: 20),
      titleLarge: style(base.titleLarge, weight: FontWeight.w600, size: 18),
      titleMedium: style(base.titleMedium, weight: FontWeight.w600, size: 16, spacing: 0.1),
      titleSmall: style(base.titleSmall, weight: FontWeight.w600, size: 14, spacing: 0.1),
      bodyLarge: style(base.bodyLarge, weight: FontWeight.w400, size: 16),
      bodyMedium: style(base.bodyMedium, weight: FontWeight.w400, size: 14),
      bodySmall: style(base.bodySmall, weight: FontWeight.w400, size: 12),
      labelLarge: style(base.labelLarge, weight: FontWeight.w600, size: 14, spacing: 0.2),
      labelMedium: style(base.labelMedium, weight: FontWeight.w600, size: 12, spacing: 0.3),
      labelSmall: style(base.labelSmall, weight: FontWeight.w600, size: 11, spacing: 0.3),
    );
  }

  static ThemeData lightTheme({Color? seed}) {
    final colorScheme = seed == null
        ? ColorScheme(
            brightness: Brightness.light,
            primary: AppColors.primary,
            onPrimary: AppColors.textOnPrimary,
            primaryContainer: const Color(0xFFCCFBF1),
            onPrimaryContainer: AppColors.primaryDark,
            secondary: AppColors.secondary,
            onSecondary: Colors.white,
            secondaryContainer: const Color(0xFFE2E8F0),
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
          )
        : ColorScheme.fromSeed(
            seedColor: seed,
            brightness: Brightness.light,
          );

    return _base(colorScheme, AppColors.background);
  }

  static ThemeData darkTheme({Color? seed}) {
    final colorScheme = seed == null
        ? ColorScheme(
            brightness: Brightness.dark,
            primary: const Color(0xFF2DD4BF),
            onPrimary: const Color(0xFF042F2E),
            primaryContainer: const Color(0xFF134E4A),
            onPrimaryContainer: const Color(0xFFCCFBF1),
            secondary: const Color(0xFF94A3B8),
            onSecondary: const Color(0xFF0F172A),
            secondaryContainer: AppColors.surfaceMutedDark,
            onSecondaryContainer: const Color(0xFFE2E8F0),
            tertiary: const Color(0xFF38BDF8),
            onTertiary: const Color(0xFF0C4A6E),
            error: const Color(0xFFF87171),
            onError: const Color(0xFF450A0A),
            surface: AppColors.surfaceDark,
            onSurface: const Color(0xFFF8FAFC),
            onSurfaceVariant: const Color(0xFF94A3B8),
            outline: const Color(0xFF64748B),
            outlineVariant: const Color(0xFF334155),
            surfaceContainerHighest: AppColors.surfaceMutedDark,
          )
        : ColorScheme.fromSeed(
            seedColor: seed,
            brightness: Brightness.dark,
          );

    return _base(colorScheme, AppColors.backgroundDark);
  }

  static ThemeData _base(ColorScheme colorScheme, Color scaffoldBg) {
    final text = _textTheme(colorScheme.onSurface);
    final buttonShape = RoundedRectangleBorder(borderRadius: AppRadius.button);

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
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: buttonShape,
          textStyle: text.labelLarge,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
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
          side: BorderSide(color: colorScheme.outlineVariant),
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
        border: OutlineInputBorder(borderRadius: AppRadius.card),
        enabledBorder: OutlineInputBorder(
          borderRadius: AppRadius.card,
          borderSide: BorderSide(color: colorScheme.outlineVariant),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: AppRadius.card,
          borderSide: BorderSide(color: colorScheme.primary, width: 1.5),
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: colorScheme.surface,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: AppRadius.card,
          side: BorderSide(color: colorScheme.outlineVariant),
        ),
        clipBehavior: Clip.antiAlias,
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: AppRadius.chip),
        side: BorderSide(color: colorScheme.outlineVariant),
        labelStyle: text.labelMedium,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      ),
      dividerTheme: DividerThemeData(
        color: colorScheme.outlineVariant,
        thickness: 1,
        space: AppSpacing.lg,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: colorScheme.surface,
        indicatorColor: colorScheme.primaryContainer,
        labelTextStyle: WidgetStatePropertyAll(text.labelSmall),
        height: 68,
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: colorScheme.surface,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.sheet),
        showDragHandle: true,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: colorScheme.surface,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.card),
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
