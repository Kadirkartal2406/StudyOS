import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/soft_progress.dart';
import '../../../../shared/widgets/study_surface.dart';
import '../../domain/entities/study_session_entity.dart';
import '../providers/study_session_provider.dart';
import '../providers/study_session_state.dart';

/// Bugün ekranı canlı Study Session — tonal, az distraction.
class LiveStudySessionCard extends ConsumerWidget {
  const LiveStudySessionCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionState = ref.watch(studySessionProvider);
    if (sessionState is! StudySessionReady || !sessionState.isLiveSession) {
      return const SizedBox.shrink();
    }

    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;
    final engine = sessionState.engineState;
    final isBreak = engine == StudyEngineState.breakTime;
    final isPaused = engine == StudyEngineState.paused;
    final accent = isBreak
        ? const Color(0xFFD97706)
        : (engine == StudyEngineState.completed
            ? scheme.primary
            : scheme.primary);
    final progress = sessionState.isChronometer
        ? (sessionState.elapsedSeconds /
                (sessionState.focusMinutes * 60).clamp(1, 24 * 3600))
            .clamp(0.0, 1.0)
        : sessionState.progress;

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.lg),
      child: StudySurface(
        color: accent.withValues(alpha: 0.10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    isBreak
                        ? 'Mola'
                        : isPaused
                            ? 'Duraklatıldı'
                            : 'Devam eden çalışma',
                    style: text.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: accent,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => context.go('/pomodoro'),
                  child: const Text('Aç'),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              sessionState.elapsedHmsLabel,
              style: text.displaySmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: -0.4,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              sessionState.displaySubject,
              style: text.titleSmall?.copyWith(fontWeight: FontWeight.w600),
            ),
            if (sessionState.displayTopic.isNotEmpty) ...[
              const SizedBox(height: 2),
              Text(
                isBreak
                    ? 'Sonraki ders · ${sessionState.displayTopic}'
                    : sessionState.displayTopic,
                style: text.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
              ),
            ],
            if (!isBreak && !sessionState.isChronometer) ...[
              const SizedBox(height: AppSpacing.sm),
              SoftProgress(value: progress, color: accent),
              const SizedBox(height: AppSpacing.xxs),
              Text(
                '%${(progress * 100).round()}',
                style: text.labelMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
              ),
            ],
            const SizedBox(height: AppSpacing.md),
            if (isBreak)
              FilledButton.tonal(
                onPressed: sessionState.isMutating
                    ? null
                    : () =>
                        ref.read(studySessionProvider.notifier).endServerBreak(),
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
    );
  }
}
