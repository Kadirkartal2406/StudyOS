import 'package:flutter/painting.dart';

/// Sprint 16 — Design tokens: spacing scale.
class AppSpacing {
  AppSpacing._();

  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;

  static const EdgeInsets page = EdgeInsets.all(md);
  static const EdgeInsets pageWide = EdgeInsets.symmetric(
    horizontal: md,
    vertical: lg,
  );
  static const EdgeInsets card = EdgeInsets.all(md);
  static const EdgeInsets cardComfortable = EdgeInsets.all(lg);
}
