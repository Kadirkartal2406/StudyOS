import 'dart:async';

import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';

/// Canlı sınav geri sayımı — tipografi odaklı, sakin.
class ExamCountdownBanner extends StatefulWidget {
  const ExamCountdownBanner({
    super.key,
    required this.examLabel,
    required this.examDate,
  });

  final String examLabel;
  final DateTime examDate;

  @override
  State<ExamCountdownBanner> createState() => _ExamCountdownBannerState();
}

class _ExamCountdownBannerState extends State<ExamCountdownBanner> {
  Timer? _timer;
  Duration _left = Duration.zero;

  @override
  void initState() {
    super.initState();
    _tick();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      final next = _compute();
      if (next != _left) setState(() => _left = next);
    });
  }

  @override
  void didUpdateWidget(covariant ExamCountdownBanner oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.examDate != widget.examDate) _tick();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _tick() => _left = _compute();

  Duration _compute() {
    final end = DateTime(
      widget.examDate.year,
      widget.examDate.month,
      widget.examDate.day,
      10,
    );
    final d = end.difference(DateTime.now());
    return d.isNegative ? Duration.zero : d;
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;
    final totalDays = _left.inDays;
    final months = totalDays ~/ 30;
    final days = totalDays % 30;
    final hours = _left.inHours % 24;
    final mins = _left.inMinutes % 60;
    final secs = _left.inSeconds % 60;

    String two(int n) => n.toString().padLeft(2, '0');

    final parts = <String>[
      if (months > 0) '$months ay',
      '$days gün',
      '${two(hours)}:${two(mins)}:${two(secs)}',
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${widget.examLabel} sınavına kalan',
          style: text.labelLarge?.copyWith(
            color: scheme.onSurfaceVariant,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          parts.join('  ·  '),
          style: text.headlineSmall?.copyWith(
            fontWeight: FontWeight.w700,
            letterSpacing: -0.2,
            fontFeatures: const [FontFeature.tabularFigures()],
          ),
        ),
      ],
    );
  }
}
