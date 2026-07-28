import 'package:flutter/material.dart';

class ConfidenceLabel {
  final String text;
  final String emoji;
  final Color color;

  const ConfidenceLabel({
    required this.text,
    required this.emoji,
    required this.color,
  });

  static ConfidenceLabel fromLevel(String level) {
    return switch (level.toLowerCase()) {
      'unknown' => const ConfidenceLabel(
          text: 'Yeni başlıyorsun',
          emoji: '🌱',
          color: Colors.grey,
        ),
      'low' => const ConfidenceLabel(
          text: 'Tekrar gerekli',
          emoji: '🔁',
          color: Colors.orange,
        ),
      'medium' => const ConfidenceLabel(
          text: 'Gelişiyor',
          emoji: '📈',
          color: Colors.blue,
        ),
      'high' => const ConfidenceLabel(
          text: 'İyi gidiyorsun',
          emoji: '⭐',
          color: Colors.green,
        ),
      'conflicted' => const ConfidenceLabel(
          text: 'Tutarsız sonuçlar',
          emoji: '⚡',
          color: Colors.deepPurple,
        ),
      _ => const ConfidenceLabel(
          text: 'Yeni başlıyorsun',
          emoji: '🌱',
          color: Colors.grey,
        ),
    };
  }
}
