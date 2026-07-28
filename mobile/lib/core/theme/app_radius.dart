import 'package:flutter/painting.dart';

/// Sprint 16 — Design tokens: radius scale.
class AppRadius {
  AppRadius._();

  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 24;

  static final BorderRadius card = BorderRadius.circular(lg);
  static final BorderRadius chip = BorderRadius.circular(sm);
  static final BorderRadius button = BorderRadius.circular(lg);
  static final BorderRadius sheet = BorderRadius.vertical(
    top: Radius.circular(xxl),
  );
}
