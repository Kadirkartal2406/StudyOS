library;

import 'package:flutter/material.dart';

class VectorStroke {
  final String id;
  final String? anchoredNodeId;
  final List<Offset> points;
  final Color color;
  final double strokeWidth;

  const VectorStroke({
    required this.id,
    this.anchoredNodeId,
    required this.points,
    required this.color,
    required this.strokeWidth,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'anchored_node_id': anchoredNodeId,
        'points': points.map((p) => [p.dx, p.dy]).toList(),
        'color': color.value,
        'stroke_width': strokeWidth,
      };
}

class EAEAnnotationManager {
  final List<VectorStroke> _strokes = [];

  List<VectorStroke> get strokes => List.unmodifiable(_strokes);

  void addStroke({
    required String id,
    required List<Offset> points,
    String? anchoredNodeId,
    Color color = Colors.amber,
    double strokeWidth = 3.0,
  }) {
    if (points.isEmpty) return;
    _strokes.add(
      VectorStroke(
        id: id,
        anchoredNodeId: anchoredNodeId,
        points: points,
        color: color,
        strokeWidth: strokeWidth,
      ),
    );
  }

  void clearNodeAnnotations(String nodeId) {
    _strokes.removeWhere((s) => s.anchoredNodeId == nodeId);
  }

  void clearAll() {
    _strokes.clear();
  }
}
