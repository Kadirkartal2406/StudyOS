import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

/// Canlı sınav geri sayımı: ay · gün · saat · dk · sn.
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

class _ExamCountdownBannerState extends State<ExamCountdownBanner>
    with SingleTickerProviderStateMixin {
  late final Ticker _ticker;
  Duration _left = Duration.zero;

  @override
  void initState() {
    super.initState();
    _tick();
    _ticker = createTicker((_) {
      if (!mounted) return;
      final next = _compute();
      if (next != _left) setState(() => _left = next);
    })
      ..start();
  }

  @override
  void didUpdateWidget(covariant ExamCountdownBanner oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.examDate != widget.examDate) _tick();
  }

  @override
  void dispose() {
    _ticker.dispose();
    super.dispose();
  }

  void _tick() => _left = _compute();

  Duration _compute() {
    final end = DateTime(
      widget.examDate.year,
      widget.examDate.month,
      widget.examDate.day,
      10, // sınav sabahı varsayılan
    );
    final d = end.difference(DateTime.now());
    return d.isNegative ? Duration.zero : d;
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final totalDays = _left.inDays;
    final months = totalDays ~/ 30;
    final days = totalDays % 30;
    final hours = _left.inHours % 24;
    final mins = _left.inMinutes % 60;
    final secs = _left.inSeconds % 60;

    String two(int n) => n.toString().padLeft(2, '0');

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: scheme.primaryContainer.withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${widget.examLabel} sınavına kalan',
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: scheme.onPrimaryContainer,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (months > 0) _chip(context, '$months', 'ay'),
              _chip(context, '$days', 'gün'),
              _chip(context, two(hours), 'saat'),
              _chip(context, two(mins), 'dk'),
              _chip(context, two(secs), 'sn'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _chip(BuildContext context, String value, String unit) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: scheme.surface,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
          ),
          Text(
            unit,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
          ),
        ],
      ),
    );
  }
}
