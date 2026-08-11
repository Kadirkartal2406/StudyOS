import 'package:flutter/painting.dart';

/// StudyOS spacing scale — generous section rhythm for editorial layouts.
class AppSpacing {
  AppSpacing._();

  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;
  static const double section = 40;

  static const EdgeInsets page = EdgeInsets.all(md);
  static const EdgeInsets pageWide = EdgeInsets.symmetric(
    horizontal: md,
    vertical: lg,
  );

  /// Home / editorial screens — more breathing room.
  static const EdgeInsets pageEditorial = EdgeInsets.symmetric(
    horizontal: md,
    vertical: xl,
  );

  static const EdgeInsets card = EdgeInsets.all(md);
  static const EdgeInsets cardComfortable = EdgeInsets.all(lg);
}
