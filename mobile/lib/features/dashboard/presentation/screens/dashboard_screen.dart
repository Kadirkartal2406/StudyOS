import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../../shared/widgets/ds.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../study_session/presentation/widgets/live_study_session_card.dart';
import '../../../study_session/presentation/widgets/today_summary_card.dart';
import '../../domain/entities/dashboard_entity.dart';
import '../providers/dashboard_provider.dart';
import '../providers/dashboard_state.dart';
import '../widgets/exam_countdown_banner.dart';
import '../widgets/goal_progress_banner.dart';
import '../widgets/notification_bell.dart';
import '../widgets/today_next_action_card.dart';
import '../../../onboarding/presentation/welcome/exam_calendar.dart';

/// RC3 — Bugün first fold: karşılama · kalan gün · sıradaki iş · bloklar.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardState = ref.watch(dashboardProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bugün'),
        actions: [
          const NotificationBell(),
          PopupMenuButton<String>(
            tooltip: 'Daha fazla',
            icon: const Icon(Icons.more_horiz),
            onSelected: (value) => context.push(value),
            itemBuilder: (context) => const [
              PopupMenuItem(value: '/assessment/daily', child: Text('Günün denemesi')),
              PopupMenuItem(value: '/score-calculator', child: Text('Tahmini puan hesapla')),
              PopupMenuItem(value: '/assessment', child: Text('Seviye testi')),
              PopupMenuItem(value: '/ai-chat', child: Text('AI sohbet')),
              PopupMenuItem(value: '/planner', child: Text('Plan önerisi')),
              PopupMenuItem(value: '/pomodoro', child: Text('Odak oturumu')),
              PopupMenuItem(value: '/exams', child: Text('Deneme sonuçları')),
              PopupMenuItem(value: '/settings', child: Text('Ayarlar')),
            ],
          ),
        ],
      ),
      body: SafeArea(
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 280),
          child: switch (dashboardState) {
            DashboardInitial() || DashboardLoading() =>
              const _TodayLoadingView(key: ValueKey('loading')),
            DashboardLoaded(:final dashboard) =>
              _TodayLoadedView(key: const ValueKey('loaded'), dashboard: dashboard),
            DashboardError(:final message) =>
              _TodayErrorView(key: const ValueKey('error'), message: message),
          },
        ),
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 0),
    );
  }
}

class _TodayLoadingView extends StatelessWidget {
  const _TodayLoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: AppSpacing.pageWide,
      children: const [
        SkeletonCard(height: 72),
        SizedBox(height: AppSpacing.md),
        SkeletonCard(height: 140),
        SizedBox(height: AppSpacing.md),
        SkeletonCard(height: 120),
      ],
    );
  }
}

class _TodayErrorView extends ConsumerWidget {
  const _TodayErrorView({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: AppSpacing.pageWide,
        child: EmptyState(
          icon: Icons.wifi_off_rounded,
          title: 'Bugün yüklenemedi',
          message: message,
          ctaLabel: 'Tekrar dene',
          onCta: () => ref.read(dashboardProvider.notifier).retry(),
        ),
      ),
    );
  }
}

class _TodayLoadedView extends ConsumerWidget {
  const _TodayLoadedView({super.key, required this.dashboard});

  final DashboardEntity dashboard;

  String _greeting(String name) {
    final h = DateTime.now().hour;
    final hi = h < 12
        ? 'Günaydın'
        : h < 18
            ? 'İyi günler'
            : 'İyi akşamlar';
    return name.isEmpty ? hi : '$hi $name';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final action = dashboard.nextAction;
    final auth = ref.watch(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final exam = (profile?.activeExamType ??
            profile?.primaryExamType ??
            dashboard.activeExamType ??
            '')
        .toUpperCase();
    final daysLeft = dashboard.journeyDaysRemaining;
    final examDate = dashboard.journeyExamDate ??
        dashboard.primaryTarget?.examDate ??
        dashboard.activeTarget?.examDate ??
        (exam.isNotEmpty ? nextExamDate(exam.toLowerCase()) : null);
    final coachLine = (dashboard.coachToday?.headline.isNotEmpty == true
            ? dashboard.coachToday!.headline
            : dashboard.coachToday?.body) ??
        dashboard.todayJourneyLine;

    return RefreshIndicator(
      onRefresh: () => ref.read(dashboardProvider.notifier).retry(),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: ListView(
            padding: AppSpacing.pageWide,
            children: [
              Text(
                _greeting(name),
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              if (exam.isNotEmpty && examDate != null) ...[
                const SizedBox(height: 10),
                ExamCountdownBanner(examLabel: exam, examDate: examDate),
                GoalProgressBanner(examLabel: exam),
              ] else if (exam.isNotEmpty) ...[
                const SizedBox(height: 6),
                Text(
                  daysLeft != null && daysLeft > 0
                      ? '$exam · $daysLeft gün kaldı'
                      : exam,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                ),
                GoalProgressBanner(examLabel: exam),
              ],
              if (coachLine != null && coachLine.trim().isNotEmpty) ...[
                const SizedBox(height: AppSpacing.md),
                Text(
                  coachLine.trim(),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        height: 1.35,
                      ),
                ),
              ],
              const SizedBox(height: AppSpacing.lg),
              const LiveStudySessionCard(),
              if (action != null)
                TodayNextActionCard(action: action)
              else
                StudyCard(
                  child: Text(
                    'Bugün için sıradaki iş henüz netleşmedi. Yenilemeyi dene.',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ),
              const SizedBox(height: AppSpacing.lg),
              Text(
                'Bugünkü bloklar',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: AppSpacing.sm),
              const TodaySummaryCard(),
              const SizedBox(height: AppSpacing.xl),
              TextButton(
                onPressed: () => context.push('/journey'),
                child: const Text('Yolculuğumu gör'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
