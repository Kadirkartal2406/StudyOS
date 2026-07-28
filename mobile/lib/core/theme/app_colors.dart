import 'package:flutter/material.dart';

/// Sprint 16 — Semantic color tokens.
/// Accent: deep teal (learning focus) — not purple/indigo cluster.
class AppColors {
  AppColors._();

  // ── Brand ─────────────────────────────────────────────────
  static const Color primary = Color(0xFF0F766E); // teal-700
  static const Color primaryDark = Color(0xFF115E59);
  static const Color secondary = Color(0xFF334155); // slate-700
  static const Color accent = Color(0xFF0EA5E9); // sky-500

  // ── Status ────────────────────────────────────────────────
  static const Color success = Color(0xFF059669);
  static const Color warning = Color(0xFFD97706);
  static const Color error = Color(0xFFDC2626);
  static const Color info = Color(0xFF0284C7);
  static const Color danger = error;

  // ── Surfaces (light) ──────────────────────────────────────
  static const Color background = Color(0xFFF1F5F9); // slate-100
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceMuted = Color(0xFFE2E8F0);
  static const Color divider = Color(0xFFCBD5E1);
  static const Color outline = Color(0xFF94A3B8);

  // ── Surfaces (dark) ───────────────────────────────────────
  static const Color backgroundDark = Color(0xFF0B1220);
  static const Color surfaceDark = Color(0xFF111827);
  static const Color surfaceMutedDark = Color(0xFF1F2937);

  // ── Text ──────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textOnPrimary = Color(0xFFFFFFFF);

  // ── Confidence spectrum ───────────────────────────────────
  static const Color confidenceHigh = Color(0xFF059669);
  static const Color confidenceMedium = Color(0xFF0EA5E9);
  static const Color confidenceLow = Color(0xFFD97706);
  static const Color confidenceUnknown = Color(0xFF94A3B8);
  static const Color confidenceConflicted = Color(0xFFDC2626);

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
