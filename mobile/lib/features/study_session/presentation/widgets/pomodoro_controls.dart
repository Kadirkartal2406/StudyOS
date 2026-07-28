import 'package:flutter/material.dart';

import '../providers/study_session_state.dart';

/// Başlat / Duraklat / Mola / Devam Et / Bitir kontrolleri.
class PomodoroControls extends StatelessWidget {
  const PomodoroControls({
    super.key,
    required this.state,
    required this.onStart,
    required this.onPause,
    required this.onResume,
    required this.onFinish,
    this.onBreak,
    this.onEndBreak,
  });

  final StudySessionReady state;
  final VoidCallback onStart;
  final VoidCallback onPause;
  final VoidCallback onResume;
  final VoidCallback onFinish;
  final VoidCallback? onBreak;
  final VoidCallback? onEndBreak;

  @override
  Widget build(BuildContext context) {
    final busy = state.isMutating;

    if (state.phase == PomodoroPhase.idle) {
      return FilledButton.icon(
        onPressed: busy ? null : onStart,
        icon: busy
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.play_arrow_rounded),
        label: const Text('Başlat'),
        style: FilledButton.styleFrom(
          minimumSize: const Size(200, 52),
        ),
      );
    }

    if (state.phase == PomodoroPhase.breakTime) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          FilledButton.icon(
            onPressed: busy ? null : (onEndBreak ?? onResume),
            icon: const Icon(Icons.play_arrow_rounded),
            label: const Text('Molayı bitir'),
          ),
          const SizedBox(width: 12),
          OutlinedButton.icon(
            onPressed: busy ? null : onFinish,
            icon: const Icon(Icons.stop_rounded),
            label: const Text('Bitir'),
          ),
        ],
      );
    }

    return Wrap(
      alignment: WrapAlignment.center,
      spacing: 12,
      runSpacing: 8,
      children: [
        if (state.isRunning) ...[
          FilledButton.tonalIcon(
            onPressed: busy ? null : onPause,
            icon: const Icon(Icons.pause_rounded),
            label: const Text('Duraklat'),
          ),
          if (onBreak != null)
            FilledButton.tonalIcon(
              onPressed: busy ? null : onBreak,
              icon: const Icon(Icons.coffee_outlined),
              label: const Text('Mola'),
            ),
        ] else
          FilledButton.icon(
            onPressed: busy ? null : onResume,
            icon: const Icon(Icons.play_arrow_rounded),
            label: const Text('Devam Et'),
          ),
        OutlinedButton.icon(
          onPressed: busy ? null : onFinish,
          icon: const Icon(Icons.stop_rounded),
          label: const Text('Bitir'),
        ),
      ],
    );
  }
}
