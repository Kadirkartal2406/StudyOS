import 'package:flutter/material.dart';

/// Büyük geri sayım + ilerleme halkası.
class PomodoroTimerRing extends StatelessWidget {
  const PomodoroTimerRing({
    super.key,
    required this.progress,
    required this.remainingLabel,
    required this.elapsedLabel,
    required this.isBreak,
  });

  final double progress;
  final String remainingLabel;
  final String elapsedLabel;
  final bool isBreak;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final ringColor = isBreak ? colorScheme.tertiary : colorScheme.primary;

    return Column(
      children: [
        SizedBox(
          width: 260,
          height: 260,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 260,
                height: 260,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 12,
                  backgroundColor: colorScheme.surfaceContainerHighest,
                  color: ringColor,
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    remainingLabel,
                    style: Theme.of(context).textTheme.displayMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                          letterSpacing: 2,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    isBreak ? 'Mola' : 'Odak',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: ringColor,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Geçen süre: $elapsedLabel',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
      ],
    );
  }
}
