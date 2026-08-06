import 'package:flutter/material.dart';
import '../asset_contracts/asset_manifest_contract.dart';

class EAEVectorCanvasPainter extends CustomPainter {
  final EAEAssetManifestContract manifest;
  final Map<String, Path> parsedPaths;
  final Set<String> selectedNodeIds;
  final Set<String> highlightedNodeIds;
  final double currentScale;
  final Color primaryHighlightColor;
  final Color selectionColor;

  EAEVectorCanvasPainter({
    required this.manifest,
    required this.parsedPaths,
    this.selectedNodeIds = const {},
    this.highlightedNodeIds = const {},
    this.currentScale = 1.0,
    this.primaryHighlightColor = const Color(0xFF2DD4BF), // StudyOS Teal
    this.selectionColor = const Color(0xFF38BDF8),        // StudyOS Sky Blue
  });

  @override
  void paint(Canvas canvas, Size size) {
    final fillPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = Colors.blueGrey.withValues(alpha: 0.15);

    final strokePaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2 / currentScale
      ..color = Colors.blueGrey.withValues(alpha: 0.6);

    final selectedPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = selectionColor.withValues(alpha: 0.6);

    final selectedStroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5 / currentScale
      ..color = selectionColor;

    final highlightPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = primaryHighlightColor.withValues(alpha: 0.5);

    for (final layer in manifest.layers) {
      if (currentScale < layer.minLod) continue;

      for (final node in layer.nodes) {
        final path = parsedPaths[node.id];
        if (path == null) continue;

        final isSelected = selectedNodeIds.contains(node.id);
        final isHighlighted = highlightedNodeIds.contains(node.id);

        if (isSelected) {
          canvas.drawPath(path, selectedPaint);
          canvas.drawPath(path, selectedStroke);
        } else if (isHighlighted) {
          canvas.drawPath(path, highlightPaint);
          canvas.drawPath(path, strokePaint);
        } else {
          canvas.drawPath(path, fillPaint);
          canvas.drawPath(path, strokePaint);
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant EAEVectorCanvasPainter oldDelegate) {
    return oldDelegate.currentScale != currentScale ||
        oldDelegate.selectedNodeIds != selectedNodeIds ||
        oldDelegate.highlightedNodeIds != highlightedNodeIds ||
        oldDelegate.manifest != manifest;
  }
}
