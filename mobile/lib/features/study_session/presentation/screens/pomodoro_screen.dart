import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../../shared/widgets/ds.dart' hide StudyCard;
import '../../../study_plan/presentation/providers/study_plan_provider.dart';
import '../../../study_plan/presentation/providers/study_plan_state.dart';
import '../../../study_plan/presentation/widgets/study_card.dart';
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
      // Server'da kalan aktif oturumu ekrana bağla (orphan 409 önleme).
      unawaited(
        ref.read(studySessionProvider.notifier).restoreActiveSession(),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(studySessionProvider);
    final notifier = ref.read(studySessionProvider.notifier);
    final code = widget.subjectCode;

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        title: const Text('Odak'),
        centerTitle: true,
        actions: [
          if (code != null && code.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: SubjectCodeChip(subjectCode: code),
            ),
        ],
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 2),
      body: StudyGlassAtmosphere(
        child: switch (state) {
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
      ),
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
            if (state.phase == PomodoroPhase.idle &&
                state.hasBlockedActiveSession) ...[
              _ActiveSessionCard(
                state: state,
                onResume: notifier.resumeBlockedSession,
                onEnd: notifier.endBlockedSession,
              ),
              const SizedBox(height: 20),
            ],
            PomodoroControls(
              state: state,
              onStart: notifier.start,
              onPause: notifier.pause,
              onResume: notifier.resume,
              onFinish: notifier.finish,
              onBreak: notifier.takeBreak,
              onEndBreak: notifier.endServerBreak,
            ),
            if (state.errorMessage != null &&
                !state.hasBlockedActiveSession) ...[
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
              const _PomodoroStudyPlanSection(),
            ],
          ],
        ),
      ),
    );
  }
}

class _ActiveSessionCard extends StatelessWidget {
  const _ActiveSessionCard({
    required this.state,
    required this.onResume,
    required this.onEnd,
  });

  final StudySessionReady state;
  final VoidCallback onResume;
  final VoidCallback onEnd;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final busy = state.isMutating;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Active Session',
              style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              state.blockedSessionTitle,
              style: theme.textTheme.bodyLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'State: ${state.blockedSessionStateLabel}',
              style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
            ),
            Text(
              'Elapsed: ${state.blockedElapsedLabel}  ·  Remaining: ${state.blockedRemainingLabel}',
              style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: busy ? null : onResume,
                    icon: const Icon(Icons.play_arrow_rounded),
                    label: const Text('Resume'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: busy ? null : onEnd,
                    icon: const Icon(Icons.stop_rounded),
                    label: const Text('End Session'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _PomodoroStudyPlanSection extends ConsumerWidget {
  const _PomodoroStudyPlanSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studyPlanProvider);
    final theme = Theme.of(context);

    if (state is! StudyPlanLoaded) {
      return const SizedBox.shrink();
    }

    final pendingPlans =
        state.plans.where((p) => p.status != 'completed').toList();

    if (pendingPlans.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 24),
        Text(
          'Bugünkü ders planın',
          style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 12),
        ...pendingPlans.take(3).map(
          (plan) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: StudyCard(
              plan: plan,
              isMutating: state.mutatingPlanId == plan.id,
              onStart: () async {
                try {
                  await ref.read(studyPlanProvider.notifier).startPlan(plan.id);
                } catch (_) {}
              },
              onStartStudy: () {
                ref.read(studySessionProvider.notifier).setContext(
                      subject: plan.subject,
                      topic: plan.topic,
                      studyPlanId: plan.id,
                    );
              },
              onComplete: () async {
                try {
                  await ref.read(studyPlanProvider.notifier).completePlan(plan.id);
                } catch (_) {}
              },
              onSkip: () async {
                try {
                  await ref.read(studyPlanProvider.notifier).skipPlan(plan.id);
                } catch (_) {}
              },
              onEdit: () {
                // TODO: Implement edit logic or navigate to edit screen
              },
              onDelete: () {
                // TODO: Implement delete logic
              },
            ),
          ),
        ),
      ],
    );
  }
}
