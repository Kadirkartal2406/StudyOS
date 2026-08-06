import 'package:flutter/material.dart';

/// Lightweight SVG Path string parser converting `d="..."` commands into native Flutter `Path` objects.
class EAEPathParser {
  /// Parses standard SVG path string data into a native Flutter `Path`.
  static Path parseSvgPathData(String svgPathData) {
    final path = Path();
    if (svgPathData.trim().isEmpty) return path;

    final regExp = RegExp(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)');
    final matches = regExp.allMatches(svgPathData);

    String currentCmd = '';
    final params = <double>[];

    for (final match in matches) {
      final token = match.group(0)!;
      if (RegExp(r'[a-zA-Z]').hasMatch(token)) {
        if (currentCmd.isNotEmpty) {
          _applyCommand(path, currentCmd, params);
          params.clear();
        }
        currentCmd = token;
      } else {
        final val = double.tryParse(token);
        if (val != null) {
          params.add(val);
        }
      }
    }

    if (currentCmd.isNotEmpty) {
      _applyCommand(path, currentCmd, params);
    }

    return path;
  }

  static void _applyCommand(Path path, String cmd, List<double> p) {
    final metric = path.computeMetrics().isEmpty
        ? null
        : path.computeMetrics().last;
    Offset cur = Offset.zero;
    if (metric != null) {
      final tangent = metric.getTangentForOffset(metric.length);
      if (tangent != null) cur = tangent.position;
    }

    switch (cmd) {
      case 'M':
        for (int i = 0; i < p.length - 1; i += 2) {
          if (i == 0) {
            path.moveTo(p[i], p[i + 1]);
          } else {
            path.lineTo(p[i], p[i + 1]);
          }
        }
        break;
      case 'm':
        for (int i = 0; i < p.length - 1; i += 2) {
          if (i == 0) {
            path.relativeMoveTo(p[i], p[i + 1]);
          } else {
            path.relativeLineTo(p[i], p[i + 1]);
          }
        }
        break;
      case 'L':
        for (int i = 0; i < p.length - 1; i += 2) {
          path.lineTo(p[i], p[i + 1]);
        }
        break;
      case 'l':
        for (int i = 0; i < p.length - 1; i += 2) {
          path.relativeLineTo(p[i], p[i + 1]);
        }
        break;
      case 'H':
        for (final x in p) {
          path.lineTo(x, cur.dy);
        }
        break;
      case 'h':
        for (final dx in p) {
          path.relativeLineTo(dx, 0);
        }
        break;
      case 'V':
        for (final y in p) {
          path.lineTo(cur.dx, y);
        }
        break;
      case 'v':
        for (final dy in p) {
          path.relativeLineTo(0, dy);
        }
        break;
      case 'C':
        for (int i = 0; i < p.length - 5; i += 6) {
          path.cubicTo(p[i], p[i + 1], p[i + 2], p[i + 3], p[i + 4], p[i + 5]);
        }
        break;
      case 'c':
        for (int i = 0; i < p.length - 5; i += 6) {
          path.relativeCubicTo(
            p[i],
            p[i + 1],
            p[i + 2],
            p[i + 3],
            p[i + 4],
            p[i + 5],
          );
        }
        break;
      case 'Q':
        for (int i = 0; i < p.length - 3; i += 4) {
          path.quadraticBezierTo(p[i], p[i + 1], p[i + 2], p[i + 3]);
        }
        break;
      case 'q':
        for (int i = 0; i < p.length - 3; i += 4) {
          path.relativeQuadraticBezierTo(p[i], p[i + 1], p[i + 2], p[i + 3]);
        }
        break;
      case 'A':
      case 'a':
        // Approximate arcs as cubic segments via path.addArc bounding oval.
        for (int i = 0; i < p.length - 6; i += 7) {
          final rx = p[i].abs();
          final ry = p[i + 1].abs();
          final x = p[i + 5];
          final y = p[i + 6];
          final end = cmd == 'a' ? Offset(cur.dx + x, cur.dy + y) : Offset(x, y);
          final rect = Rect.fromCenter(
            center: Offset((cur.dx + end.dx) / 2, (cur.dy + end.dy) / 2),
            width: rx * 2,
            height: ry * 2,
          );
          path.arcToPoint(
            end,
            radius: Radius.elliptical(rx, ry),
            largeArc: p[i + 3] != 0,
            clockwise: p[i + 4] == 0,
          );
          // keep analyzer happy with rect usage in debug builds
          assert(rect.width >= 0);
          cur = end;
        }
        break;
      case 'Z':
      case 'z':
        path.close();
        break;
      default:
        if (p.length >= 2) {
          path.moveTo(p[0], p[1]);
        }
    }
  }
}
