import 'package:flutter/material.dart';
import '../asset_contracts/asset_manifest_contract.dart';
import 'providers/eae_render_provider.dart';

class EAEVectorCanvasPainter extends CustomPainter {
  final EAEAssetManifestContract manifest;
  final Map<String, Path> parsedPaths;
  final Set<String> selectedNodeIds;
  final Set<String> highlightedNodeIds;
  final Set<String> matchedNodeIds;
  final String? activeQuestionNodeId;
  final double currentScale;
  final EAEInteractionMode interactionMode;
  final Color primaryHighlightColor;
  final Color selectionColor;
  final Color matchedColor;
  final Color errorColor;

  EAEVectorCanvasPainter({
    required this.manifest,
    required this.parsedPaths,
    this.selectedNodeIds = const {},
    this.highlightedNodeIds = const {},
    this.matchedNodeIds = const {},
    this.activeQuestionNodeId,
    this.currentScale = 1.0,
    this.interactionMode = EAEInteractionMode.explore,
    this.primaryHighlightColor = const Color(0xFF2DD4BF),
    this.selectionColor = const Color(0xFF38BDF8),
    this.matchedColor = const Color(0xFF4ADE80),
    this.errorColor = const Color(0xFFF87171),
  });

  static const _palette = [
    Color(0xFFFFB3BA), // Pastel Red
    Color(0xFFFFDFBA), // Pastel Orange
    Color(0xFFFFFFBA), // Pastel Yellow
    Color(0xFFBAFFC9), // Pastel Green
    Color(0xFFBAE1FF), // Pastel Blue
    Color(0xFFE2C9FF), // Pastel Purple
    Color(0xFFFFC9DE), // Pastel Pink
    Color(0xFFD4F0F0), // Mint
    Color(0xFFFBE4E4), // Peach
  ];

  @override
  void paint(Canvas canvas, Size size) {

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

    final matchedPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = matchedColor.withValues(alpha: 0.7);

    final matchedStroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5 / currentScale
      ..color = matchedColor;

    final questionStroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0 / currentScale
      ..color = primaryHighlightColor;

    for (final layer in manifest.layers) {
      if (currentScale < layer.minLod) continue;

      for (final node in layer.nodes) {
        final path = parsedPaths[node.id];
        if (path == null) continue;

        final isSelected = selectedNodeIds.contains(node.id);
        final isHighlighted = highlightedNodeIds.contains(node.id);
        final isMatched = matchedNodeIds.contains(node.id);
        final isQuestion = activeQuestionNodeId == node.id;

        if (isMatched) {
          canvas.drawPath(path, matchedPaint);
          canvas.drawPath(path, matchedStroke);
        } else if (isSelected) {
          canvas.drawPath(path, selectedPaint);
          canvas.drawPath(path, selectedStroke);
        } else if (isHighlighted) {
          canvas.drawPath(path, highlightPaint);
          canvas.drawPath(path, strokePaint);
        } else {
          // If in an exam or match mode and NOT matched, grey it out slightly unless free exploration
          if (interactionMode == EAEInteractionMode.match || 
              interactionMode == EAEInteractionMode.exam ||
              interactionMode == EAEInteractionMode.dragDrop) {
            final emptyFill = Paint()
              ..style = PaintingStyle.fill
              ..color = Colors.blueGrey.withValues(alpha: 0.1);
            canvas.drawPath(path, emptyFill);
            canvas.drawPath(path, strokePaint);
          } else {
            final colorIndex = node.id.hashCode.abs() % _palette.length;
            final dynamicFill = Paint()
              ..style = PaintingStyle.fill
              ..color = _palette[colorIndex];
            
            canvas.drawPath(path, dynamicFill);
            canvas.drawPath(path, strokePaint);
          }
        }

        if (isQuestion) {
           canvas.drawPath(path, questionStroke);
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant EAEVectorCanvasPainter oldDelegate) {
    return oldDelegate.currentScale != currentScale ||
        oldDelegate.selectedNodeIds != selectedNodeIds ||
        oldDelegate.highlightedNodeIds != highlightedNodeIds ||
        oldDelegate.matchedNodeIds != matchedNodeIds ||
        oldDelegate.activeQuestionNodeId != activeQuestionNodeId ||
        oldDelegate.interactionMode != interactionMode ||
        oldDelegate.manifest != manifest;
  }
}
