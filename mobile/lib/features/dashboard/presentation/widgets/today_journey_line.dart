import 'package:flutter/material.dart';

/// Alignment Sprint-1 — mikro Journey satırı (bağlam; panel değil).
class TodayJourneyLine extends StatelessWidget {
  const TodayJourneyLine({super.key, this.line});

  final String? line;

  @override
  Widget build(BuildContext context) {
    final text = line?.trim();
    if (text == null || text.isEmpty) return const SizedBox.shrink();

    return Text(
      text,
      style: Theme.of(context).textTheme.labelMedium?.copyWith(
            color: Theme.of(context).colorScheme.outline,
          ),
    );
  }
}
