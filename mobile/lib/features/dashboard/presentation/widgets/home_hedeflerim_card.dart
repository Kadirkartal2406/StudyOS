import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_floating_card.dart';
import '../../../../shared/widgets/study_glass_button.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Hedeflerim home section — circular progress + liquid glass.
class HomeHedeflerimCard extends StatelessWidget {
  const HomeHedeflerimCard({super.key, required this.dashboard});

  final DashboardEntity dashboard;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final dark = Theme.of(context).brightness == Brightness.dark;
    final pct = dashboard.dailyProgressPercentage.clamp(0.0, 100.0);
    final ring = (pct / 100).clamp(0.0, 1.0);
    final focus = dashboard.todayStudyMinutes;
    final goal = dashboard.dailyStudyGoalMinutes;
    final questions = dashboard.todayQuestionsSolved;
    final questionTarget = questions < 70 ? 70 : ((questions / 10).ceil() * 10);
    final accuracy = dashboard.lastExamNet != null
        ? ((dashboard.lastExamNet! / 40) * 100).clamp(0, 100).round()
        : dashboard.journeyWeekPct.round().clamp(0, 100);

    return StudyFloatingCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Hedeflerim',
            style: text.titleLarge?.copyWith(
              color: scheme.onSurface,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Center(
            child: SizedBox(
              width: 168,
              height: 168,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 168,
                    height: 168,
                    child: CircularProgressIndicator(
                      value: ring,
                      strokeWidth: 14,
                      strokeCap: StrokeCap.round,
                      backgroundColor: dark
                          ? Colors.white.withValues(alpha: 0.12)
                          : AppColors.divider,
                      color: scheme.primary,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          '${pct.round()}%',
                          style: text.headlineLarge?.copyWith(
                            fontWeight: FontWeight.w800,
                            letterSpacing: -0.8,
                            color: scheme.onSurface,
                          ),
                        ),
                        Text(
                          'Günlük Hedef\nTamamlandı',
                          textAlign: TextAlign.center,
                          style: text.labelMedium?.copyWith(
                            color: scheme.onSurfaceVariant,
                            height: 1.25,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          _GoalStat(
            label: 'Çalışma Süresi',
            value: '$focus / $goal dk',
          ),
          const SizedBox(height: AppSpacing.sm),
          _GoalStat(
            label: 'Soru Çözme',
            value: '$questions / $questionTarget',
          ),
          const SizedBox(height: AppSpacing.sm),
          _GoalStat(
            label: 'Doğru Oranı',
            value: '%$accuracy',
          ),
          const SizedBox(height: AppSpacing.md),
          StudyGlassButton(
            label: 'Hedefleri Gör',
            leadingIcon: StudyIcons.statistics,
            variant: StudyGlassVariant.secondary,
            size: StudyGlassSize.medium,
            onPressed: () => context.push('/journey'),
          ),
        ],
      ),
    );
  }
}

class _GoalStat extends StatelessWidget {
  const _GoalStat({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: text.bodyLarge?.copyWith(
              color: scheme.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Text(
          value,
          style: text.titleSmall?.copyWith(
            color: scheme.onSurface,
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }
}
