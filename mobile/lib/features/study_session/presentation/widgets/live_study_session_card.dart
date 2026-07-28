import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../domain/entities/study_session_entity.dart';
import '../providers/study_session_provider.dart';
import '../providers/study_session_state.dart';

/// M25 — Bugün ekranı canlı Study Session kartı.
class LiveStudySessionCard extends ConsumerWidget {
  const LiveStudySessionCard({super.key});

  static const _studyGreen = Color(0xFF1B7A5A);
  static const _studyBlue = Color(0xFF1E6B8A);
  static const _breakOrange = Color(0xFFE67E22);
  static const _doneGreen = Color(0xFF2E8B57);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionState = ref.watch(studySessionProvider);
    if (sessionState is! StudySessionReady || !sessionState.isLiveSession) {
      return const SizedBox.shrink();
    }

    final engine = sessionState.engineState;
    final isBreak = engine == StudyEngineState.breakTime;
    final isPaused = engine == StudyEngineState.paused;
    final accent = isBreak
        ? _breakOrange
        : (engine == StudyEngineState.completed ? _doneGreen : _studyGreen);
    final secondary =
        isBreak ? _breakOrange.withValues(alpha: 0.85) : _studyBlue;
    final progress = sessionState.isChronometer
        ? (sessionState.elapsedSeconds /
                (sessionState.focusMinutes * 60).clamp(1, 24 * 3600))
            .clamp(0.0, 1.0)
        : sessionState.progress;

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.lg),
      child: AnimatedScale(
        scale: sessionState.isRunning ? 1.02 : 1.0,
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOutCubic,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 420),
          curve: Curves.easeInOut,
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                accent.withValues(alpha: 0.14),
                secondary.withValues(alpha: 0.08),
              ],
            ),
            border: Border.all(color: accent.withValues(alpha: 0.35)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    isBreak ? '☕' : '📚',
                    style: const TextStyle(fontSize: 22),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      isBreak
                          ? 'Mola'
                          : isPaused
                              ? 'Duraklatıldı'
                              : 'Bugünkü Çalışma',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                            color: accent,
                          ),
                    ),
                  ),
                  TextButton(
                    onPressed: () => context.push('/pomodoro'),
                    child: const Text('Aç'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                sessionState.elapsedHmsLabel,
                style: Theme.of(context).textTheme.displaySmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.2,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
              ),
              const SizedBox(height: 6),
              Text(
                sessionState.displaySubject,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              if (sessionState.displayTopic.isNotEmpty) ...[
                const SizedBox(height: 2),
                Text(
                  isBreak
                      ? 'Sonraki ders · ${sessionState.displayTopic}'
                      : sessionState.displayTopic,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
              if (!isBreak && !sessionState.isChronometer) ...[
                const SizedBox(height: AppSpacing.sm),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 8,
                    backgroundColor: accent.withValues(alpha: 0.15),
                    color: accent,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '%${(progress * 100).round()}',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
              ],
              const SizedBox(height: AppSpacing.md),
              if (isBreak)
                FilledButton.tonal(
                  onPressed: sessionState.isMutating
                      ? null
                      : () => ref
                          .read(studySessionProvider.notifier)
                          .endServerBreak(),
                  child: const Text('Derse Dön'),
                )
              else if (!isPaused)
                FilledButton.tonal(
                  onPressed: sessionState.isMutating
                      ? null
                      : () =>
                          ref.read(studySessionProvider.notifier).takeBreak(),
                  child: const Text('Molaya Çık'),
                )
              else
                FilledButton.tonal(
                  onPressed: sessionState.isMutating
                      ? null
                      : () => ref.read(studySessionProvider.notifier).resume(),
                  child: const Text('Devam Et'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
