import 'package:flutter/material.dart';

/// Local scratch pad (pen / eraser) — not persisted.
class MathScratchPad extends StatefulWidget {
  const MathScratchPad({super.key});

  @override
  State<MathScratchPad> createState() => _MathScratchPadState();
}

class _MathScratchPadState extends State<MathScratchPad> {
  final List<_Stroke> _strokes = [];
  _Stroke? _current;
  bool _eraser = false;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final bg = scheme.surfaceContainerHighest.withValues(alpha: 0.45);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            IconButton(
              tooltip: 'Kalem',
              onPressed: () => setState(() => _eraser = false),
              icon: Icon(
                Icons.edit,
                color: _eraser ? scheme.onSurfaceVariant : scheme.primary,
              ),
            ),
            IconButton(
              tooltip: 'Silgi',
              onPressed: () => setState(() => _eraser = true),
              icon: Icon(
                Icons.cleaning_services_outlined,
                color: _eraser ? scheme.primary : scheme.onSurfaceVariant,
              ),
            ),
            IconButton(
              tooltip: 'Temizle',
              onPressed: () => setState(() {
                _strokes.clear();
                _current = null;
              }),
              icon: const Icon(Icons.delete_outline),
            ),
            const Spacer(),
            Text(
              'Çizim alanı',
              style: Theme.of(context).textTheme.labelMedium,
            ),
          ],
        ),
        Expanded(
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: bg,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: scheme.outlineVariant),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: GestureDetector(
                onPanStart: (d) {
                  setState(() {
                    _current = _Stroke(
                      points: [d.localPosition],
                      erase: _eraser,
                    );
                    _strokes.add(_current!);
                  });
                },
                onPanUpdate: (d) {
                  setState(() {
                    _current?.points.add(d.localPosition);
                  });
                },
                onPanEnd: (_) => _current = null,
                child: CustomPaint(
                  painter: _PadPainter(_strokes, bg),
                  child: const SizedBox.expand(),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _Stroke {
  _Stroke({required this.points, required this.erase});
  final List<Offset> points;
  final bool erase;
}

class _PadPainter extends CustomPainter {
  _PadPainter(this.strokes, this.bg);
  final List<_Stroke> strokes;
  final Color bg;

  @override
  void paint(Canvas canvas, Size size) {
    for (final s in strokes) {
      final paint = Paint()
        ..color = s.erase ? bg : Colors.black87
        ..strokeWidth = s.erase ? 18 : 2.4
        ..strokeCap = StrokeCap.round
        ..style = PaintingStyle.stroke;
      for (var i = 0; i < s.points.length - 1; i++) {
        canvas.drawLine(s.points[i], s.points[i + 1], paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _PadPainter oldDelegate) => true;
}
