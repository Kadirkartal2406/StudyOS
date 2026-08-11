import 'package:flutter/painting.dart';

/// StudyOS radius scale — soft cards + capsule CTAs.
class AppRadius {
  AppRadius._();

  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 24;
  static const double hero = 28;
  /// Full pill for Glass / Floating buttons.
  static const double capsule = 999;

  static final BorderRadius card = BorderRadius.circular(lg);
  static final BorderRadius chip = BorderRadius.circular(sm);
  static final BorderRadius button = BorderRadius.circular(lg);
  static final BorderRadius capsuleButton = BorderRadius.circular(capsule);
  static final BorderRadius surface = BorderRadius.circular(xl);
  static final BorderRadius heroImage = BorderRadius.circular(hero);
  static final BorderRadius sheet = const BorderRadius.vertical(
    top: Radius.circular(xxl),
  );
}
