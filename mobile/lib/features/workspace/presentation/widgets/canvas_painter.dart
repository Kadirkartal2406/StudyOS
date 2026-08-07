import 'package:flutter/material.dart';
import '../../domain/entities/annotation_object.dart';
import '../providers/workspace_provider.dart';

class CanvasPainter extends CustomPainter {
  final List<AnnotationObject> objects;
  final List<Offset> currentStroke;
  final DrawingTool currentTool;
  final Color currentColor;
  final double currentStrokeWidth;

  CanvasPainter({
    required this.objects,
    required this.currentStroke,
    required this.currentTool,
    required this.currentColor,
    required this.currentStrokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Draw existing objects
    for (final obj in objects) {
      if (obj is StrokeObject) {
        final paint = Paint()
          ..color = obj.color
          ..strokeWidth = obj.strokeWidth
          ..strokeCap = StrokeCap.round
          ..strokeJoin = StrokeJoin.round
          ..style = PaintingStyle.stroke;

        if (obj.points.length > 1) {
          final path = Path()..moveTo(obj.points.first.dx, obj.points.first.dy);
          for (int i = 1; i < obj.points.length; i++) {
            path.lineTo(obj.points[i].dx, obj.points[i].dy);
          }
          canvas.drawPath(path, paint);
        } else if (obj.points.isNotEmpty) {
          canvas.drawPoints(PointMode.points, obj.points, paint);
        }
      } else if (obj is TextObject) {
        final textPainter = TextPainter(
          text: TextSpan(
            text: obj.text,
            style: TextStyle(color: obj.color, fontSize: obj.fontSize),
          ),
          textDirection: TextDirection.ltr,
        );
        textPainter.layout();
        textPainter.paint(canvas, obj.position);
      }
      // Note: EAE objects are typically rendered as Widgets in an InteractiveViewer Stack
      // rather than painted directly to CustomPainter, for performance and interaction.
    }

    // 2. Draw current active stroke
    if (currentStroke.isNotEmpty && 
        (currentTool == DrawingTool.pen || currentTool == DrawingTool.highlighter)) {
      final isHighlighter = currentTool == DrawingTool.highlighter;
      final paint = Paint()
        ..color = isHighlighter ? currentColor.withOpacity(0.3) : currentColor
        ..strokeWidth = isHighlighter ? currentStrokeWidth * 3 : currentStrokeWidth
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round
        ..style = PaintingStyle.stroke;

      final path = Path()..moveTo(currentStroke.first.dx, currentStroke.first.dy);
      for (int i = 1; i < currentStroke.length; i++) {
        path.lineTo(currentStroke[i].dx, currentStroke[i].dy);
      }
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CanvasPainter oldDelegate) {
    return oldDelegate.objects != objects ||
           oldDelegate.currentStroke != currentStroke ||
           oldDelegate.currentTool != currentTool ||
           oldDelegate.currentColor != currentColor ||
           oldDelegate.currentStrokeWidth != currentStrokeWidth;
  }
}
