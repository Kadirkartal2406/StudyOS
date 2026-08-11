import 'package:flutter/material.dart';

import 'app_colors.dart';

/// Soft, sparse elevation — Glass / Floating surfaces.
class AppShadows {
  AppShadows._();

  static List<BoxShadow> get soft => const [
        BoxShadow(
          color: AppColors.shadow,
          blurRadius: 24,
          offset: Offset(0, 8),
        ),
      ];

  /// Primary floating CTA — subtle lift, not heavy Material elevation.
  static List<BoxShadow> get floating => const [
        BoxShadow(
          color: AppColors.shadowSoft,
          blurRadius: 20,
          offset: Offset(0, 6),
        ),
        BoxShadow(
          color: AppColors.shadowSoft,
          blurRadius: 6,
          offset: Offset(0, 2),
        ),
      ];

  /// iOS liquid-glass depth — soft ambient + tight contact.
  static List<BoxShadow> get liquid => const [
        BoxShadow(
          color: Color(0x140F172A),
          blurRadius: 28,
          spreadRadius: -4,
          offset: Offset(0, 12),
        ),
        BoxShadow(
          color: Color(0x0A0F172A),
          blurRadius: 8,
          offset: Offset(0, 2),
        ),
      ];

  /// Stronger liquid depth for premium panels (iOS 26-like float).
  static List<BoxShadow> get liquidDeep => const [
        BoxShadow(
          color: Color(0x1A0F172A),
          blurRadius: 40,
          spreadRadius: -6,
          offset: Offset(0, 18),
        ),
        BoxShadow(
          color: Color(0x120F766E),
          blurRadius: 24,
          offset: Offset(0, 8),
        ),
        BoxShadow(
          color: Color(0x0F0F172A),
          blurRadius: 6,
          offset: Offset(0, 2),
        ),
      ];

  static List<BoxShadow> get floatingPressed => const [
        BoxShadow(
          color: AppColors.shadowSoft,
          blurRadius: 10,
          offset: Offset(0, 3),
        ),
      ];

  static List<BoxShadow> get sheet => const [
        BoxShadow(
          color: AppColors.shadow,
          blurRadius: 32,
          offset: Offset(0, -4),
        ),
      ];
}
