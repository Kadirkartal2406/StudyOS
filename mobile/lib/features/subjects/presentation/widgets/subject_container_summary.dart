import 'package:flutter/material.dart';

import '../../domain/entities/subject_hub_entity.dart';

/// Alignment Sprint-2 — kısa Subject özeti (kart yığını değil).
class SubjectContainerSummary extends StatelessWidget {
  const SubjectContainerSummary({
    super.key,
    required this.progress,
    required this.today,
  });

  final SubjectHubProgress progress;
  final SubjectHubToday today;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final parts = <String>[
      '%${progress.progressPct.clamp(0, 100).toStringAsFixed(0)} ilerleme',
      if (today.studyMinutes > 0)
        'Bugün ${today.studyMinutes} dk'
      else
        'Bugün henüz çalışma yok',
    ];

    return Text(
      parts.join(' · '),
      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
    );
  }
}
