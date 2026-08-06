import 'package:flutter/material.dart';

class EAEViewportState {
  final Matrix4 transform;
  final double scale;
  final Offset translation;

  const EAEViewportState({
    required this.transform,
    this.scale = 1.0,
    this.translation = Offset.zero,
  });

  EAEViewportState copyWith({
    Matrix4? transform,
    double? scale,
    Offset? translation,
  }) {
    return EAEViewportState(
      transform: transform ?? this.transform,
      scale: scale ?? this.scale,
      translation: translation ?? this.translation,
    );
  }
}

class EAEViewportController extends ValueNotifier<EAEViewportState> {
  final double minScale;
  final double maxScale;

  EAEViewportController({
    this.minScale = 1.0,
    this.maxScale = 8.0,
  }) : super(EAEViewportState(transform: Matrix4.identity()));

  void reset() {
    value = EAEViewportState(transform: Matrix4.identity());
  }

  void updateTransform(Matrix4 newTransform) {
    final scale = newTransform.getMaxScaleOnAxis();
    final clampedScale = scale.clamp(minScale, maxScale);

    final translation = Offset(
      newTransform.getTranslation().x,
      newTransform.getTranslation().y,
    );

    value = EAEViewportState(
      transform: newTransform,
      scale: clampedScale,
      translation: translation,
    );
  }
}
