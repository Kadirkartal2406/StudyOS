import 'package:flutter/material.dart';

/// Alignment Sprint-1 — bağlam satırları. Asla ikinci CTA değildir.
class TodayContextLines extends StatelessWidget {
  const TodayContextLines({super.key, required this.lines});

  final List<String> lines;

  @override
  Widget build(BuildContext context) {
    if (lines.isEmpty) return const SizedBox.shrink();

    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final line in lines) ...[
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(
              '• $line',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
          ),
        ],
      ],
    );
  }
}
