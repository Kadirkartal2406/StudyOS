import 'package:flutter/material.dart';

import '../../domain/entities/pomodoro_preset.dart';

/// Hazır süre paketleri + özel süre girişi.
class PomodoroPresetSelector extends StatelessWidget {
  const PomodoroPresetSelector({
    super.key,
    required this.focusMinutes,
    required this.breakMinutes,
    required this.enabled,
    required this.onPresetSelected,
    required this.onCustomSelected,
  });

  final int focusMinutes;
  final int breakMinutes;
  final bool enabled;
  final ValueChanged<PomodoroPreset> onPresetSelected;
  final VoidCallback onCustomSelected;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      alignment: WrapAlignment.center,
      children: [
        for (final preset in PomodoroPreset.defaults)
          ChoiceChip(
            label: Text(preset.label),
            selected: focusMinutes == preset.focusMinutes &&
                breakMinutes == preset.breakMinutes,
            onSelected: enabled
                ? (_) => onPresetSelected(preset)
                : null,
          ),
        ActionChip(
          avatar: const Icon(Icons.tune, size: 18),
          label: const Text('Özel'),
          onPressed: enabled ? onCustomSelected : null,
        ),
      ],
    );
  }
}
