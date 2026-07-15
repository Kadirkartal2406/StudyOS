import 'package:flutter/material.dart';

/// StudyOS renk paleti.
/// Tasarım sistemi Sprint-1.2'de genişletilecek.
class AppColors {
  AppColors._();

  // ── Marka Renkleri ──────────────────────────────────────
  static const Color primary = Color(0xFF4F46E5);     // Indigo
  static const Color primaryDark = Color(0xFF3730A3);
  static const Color secondary = Color(0xFF06B6D4);   // Cyan
  static const Color accent = Color(0xFF8B5CF6);      // Violet

  // ── Durum Renkleri ──────────────────────────────────────
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);

  // ── Nötr Renkler ────────────────────────────────────────
  static const Color surface = Color(0xFFF9FAFB);
  static const Color surfaceDark = Color(0xFF1F2937);
  static const Color border = Color(0xFFE5E7EB);
  static const Color textPrimary = Color(0xFF111827);
  static const Color textSecondary = Color(0xFF6B7280);
}
