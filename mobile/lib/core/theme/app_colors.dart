import 'package:flutter/material.dart';

/// StudyOS semantic color tokens — teal brand, Glass/Floating system.
class AppColors {
  AppColors._();

  // ── Brand (D — Glass reference) ───────────────────────────
  static const Color primary = Color(0xFF0F766E); // teal-700
  static const Color primaryDark = Color(0xFF115E59);
  static const Color primaryLight = Color(0xFF14B8A6); // teal soft
  static const Color secondary = Color(0xFF334155); // slate-700
  static const Color accent = Color(0xFF0EA5E9); // sky-500

  // ── Status (solid — for icons/progress; soft tints below) ─
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);
  static const Color danger = error;

  // Soft / tonal fills for glass secondary actions (low alpha on white)
  static const Color successSoft = Color(0x1A22C55E);
  static const Color warningSoft = Color(0x1AF59E0B);
  static const Color errorSoft = Color(0x1AEF4444);
  static const Color infoSoft = Color(0x1A3B82F6);
  static const Color primarySoft = Color(0x1A0F766E);
  static const Color primarySoftBorder = Color(0x330F766E);

  // ── Surfaces (light) ──────────────────────────────────────
  static const Color background = Color(0xFFF7F8FA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceMuted = Color(0xFFEEF1F5);
  static const Color surfaceTonal = Color(0xFFF0F4F3);
  static const Color glassFill = Color(0xE6FFFFFF); // ~90% white
  static const Color divider = Color(0xFFE2E8F0);
  static const Color outline = Color(0xFF94A3B8);

  // Liquid glass fills — denser + luminous (web needs stronger base)
  static const Color liquidGlassLight = Color(0xCCFFFFFF); // ~80% white
  static const Color liquidGlassDark = Color(0xB31E293B); // ~70% slate
  static const Color liquidGlassEdgeLight = Color(0x99FFFFFF);
  static const Color liquidGlassEdgeDark = Color(0x4DFFFFFF);

  // ── Surfaces (dark) ───────────────────────────────────────
  static const Color backgroundDark = Color(0xFF0B1220);
  static const Color surfaceDark = Color(0xFF111827);
  static const Color surfaceMutedDark = Color(0xFF1F2937);
  static const Color surfaceTonalDark = Color(0xFF15202B);
  static const Color glassFillDark = Color(0xCC1F2937);

  // ── Text ──────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  static const Color textPrimaryDark = Color(0xFFF8FAFC);
  static const Color textSecondaryDark = Color(0xFF94A3B8);

  /// Theme-aware primary body text (fixes dark-mode invisible labels).
  static Color onSurfaceOf(Brightness brightness) =>
      brightness == Brightness.dark ? textPrimaryDark : textPrimary;

  /// Theme-aware secondary / muted text.
  static Color onSurfaceVariantOf(Brightness brightness) =>
      brightness == Brightness.dark ? textSecondaryDark : textSecondary;

  // ── Shadows ───────────────────────────────────────────────
  static const Color shadow = Color(0x1A0F172A);
  static const Color shadowSoft = Color(0x140F172A);

  // ── Confidence spectrum ───────────────────────────────────
  static const Color confidenceHigh = Color(0xFF22C55E);
  static const Color confidenceMedium = Color(0xFF3B82F6);
  static const Color confidenceLow = Color(0xFFF59E0B);
  static const Color confidenceUnknown = Color(0xFF94A3B8);
  static const Color confidenceConflicted = Color(0xFFEF4444);

  static Color confidenceOf(String level) {
    return switch (level.toLowerCase()) {
      'high' => confidenceHigh,
      'medium' => confidenceMedium,
      'low' => confidenceLow,
      'conflicted' => confidenceConflicted,
      _ => confidenceUnknown,
    };
  }

  static Color toneOf(String tone) {
    return switch (tone.toLowerCase()) {
      'positive' => success,
      'caution' => warning,
      'danger' => danger,
      _ => info,
    };
  }
}
