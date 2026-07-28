import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../subjects/presentation/widgets/subject_code_chip.dart';
import '../providers/study_session_provider.dart';
import '../providers/study_session_state.dart';
import '../widgets/pomodoro_controls.dart';
import '../widgets/pomodoro_preset_selector.dart';
import '../widgets/pomodoro_timer_ring.dart';
import '../widgets/today_summary_card.dart';

/// Pomodoro (Study Session) ana ekranı.
class PomodoroScreen extends ConsumerStatefulWidget {
  const PomodoroScreen({
    super.key,
    this.subjectCode,
    this.topicCode,
    this.topicName,
  });

  /// LOS: Canonical kodlar — Evidence binding için.
  final String? subjectCode;
  final String? topicCode;
  final String? topicName;

  @override
  ConsumerState<PomodoroScreen> createState() => _PomodoroScreenState();
}

class _PomodoroScreenState extends ConsumerState<PomodoroScreen> {
  @override
  void initState() {
    super.initState();
    // Oturum başlamadan konu bağlamını ata (LOS Evidence binding)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final code = widget.subjectCode;
      final topic = widget.topicCode;
      if (code != null || topic != null) {
        ref.read(studySessionProvider.notifier).setContext(
              subjectCode: code,
              topicCode: topic,
              subject: code,
              topic: widget.topicName ?? topic,
            );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(studySessionProvider);
    final notifier = ref.read(studySessionProvider.notifier);
    final code = widget.subjectCode;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Pomodoro'),
        centerTitle: true,
        actions: [
          if (code != null && code.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: SubjectCodeChip(subjectCode: code),
            ),
        ],
      ),
      body: switch (state) {
        StudySessionInitial() => const Center(
            child: CircularProgressIndicator(),
          ),
        StudySessionError(:final message) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(message, textAlign: TextAlign.center),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () =>
                        ref.invalidate(studySessionProvider),
                    child: const Text('Yeniden Dene'),
                  ),
                ],
              ),
            ),
          ),
        StudySessionReady() => _PomodoroBody(
            state: state,
            notifier: notifier,
          ),
      },
    );
  }
}

class _PomodoroBody extends StatelessWidget {
  const _PomodoroBody({
    required this.state,
    required this.notifier,
  });

  final StudySessionReady state;
  final StudySessionNotifier notifier;

  Future<void> _showCustomDialog(BuildContext context) async {
    final focusController =
        TextEditingController(text: '${state.focusMinutes}');
    final breakController =
        TextEditingController(text: '${state.breakMinutes}');

    final result = await showDialog<({int focus, int breakMinutes})>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Özel süre'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: focusController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Odak (dakika)',
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: breakController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Mola (dakika)',
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('İptal'),
            ),
            FilledButton(
              onPressed: () {
                final focus = int.tryParse(focusController.text) ?? 0;
                final breakMinutes = int.tryParse(breakController.text) ?? 0;
                Navigator.pop(
                  context,
                  (focus: focus, breakMinutes: breakMinutes),
                );
              },
              child: const Text('Uygula'),
            ),
          ],
        );
      },
    );

    if (result != null) {
      notifier.setCustomDuration(
        focusMinutes: result.focus,
        breakMinutes: result.breakMinutes,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final canEditPreset = state.phase == PomodoroPhase.idle && !state.isMutating;

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          children: [
            if (state.subject != null || state.topic != null) ...[
              Card(
                child: ListTile(
                  leading: Icon(
                    Icons.menu_book_rounded,
                    color: colorScheme.primary,
                  ),
                  title: Text(state.subject ?? 'Serbest çalışma'),
                  subtitle: state.topic != null ? Text(state.topic!) : null,
                ),
              ),
              const SizedBox(height: 16),
            ],
            if (state.phase == PomodoroPhase.breakTime)
              Chip(
                avatar: Icon(
                  Icons.coffee_rounded,
                  color: colorScheme.tertiary,
                  size: 18,
                ),
                label: const Text('Mola zamanı'),
              ),
            const SizedBox(height: 8),
            SegmentedButton<bool>(
              segments: const [
                ButtonSegment(value: false, label: Text('Pomodoro'), icon: Icon(Icons.timer_outlined)),
                ButtonSegment(value: true, label: Text('Kronometre'), icon: Icon(Icons.av_timer)),
              ],
              selected: {state.isChronometer},
              onSelectionChanged: canEditPreset
                  ? (s) => notifier.setChronometerMode(s.first)
                  : null,
            ),
            const SizedBox(height: 16),
            PomodoroTimerRing(
              progress: state.isChronometer && state.phase == PomodoroPhase.focus
                  ? 0
                  : state.progress,
              remainingLabel: state.isChronometer && state.phase == PomodoroPhase.focus
                  ? state.elapsedLabel
                  : state.remainingLabel,
              elapsedLabel: state.elapsedLabel,
              isBreak: state.phase == PomodoroPhase.breakTime,
            ),
            const SizedBox(height: 24),
            if (!state.isChronometer)
              PomodoroPresetSelector(
                focusMinutes: state.focusMinutes,
                breakMinutes: state.breakMinutes,
                enabled: canEditPreset,
                onPresetSelected: notifier.selectPreset,
                onCustomSelected: () => _showCustomDialog(context),
              ),
            const SizedBox(height: 28),
            PomodoroControls(
              state: state,
              onStart: notifier.start,
              onPause: notifier.pause,
              onResume: notifier.resume,
              onFinish: notifier.finish,
              onBreak: notifier.takeBreak,
              onEndBreak: notifier.endServerBreak,
            ),
            if (state.errorMessage != null) ...[
              const SizedBox(height: 16),
              Text(
                state.errorMessage!,
                style: TextStyle(color: colorScheme.error),
                textAlign: TextAlign.center,
              ),
            ],
            const SizedBox(height: 24),
            Text(
              'Kalan: ${state.remainingLabel}  ·  Geçen: ${state.elapsedLabel}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            if (state.phase == PomodoroPhase.idle) ...[
              const SizedBox(height: 24),
              const TodaySummaryCard(),
            ],
          ],
        ),
      ),
    );
  }
}
