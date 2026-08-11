import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../../shared/widgets/ds.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../study_session/presentation/widgets/live_study_session_card.dart';
import '../../domain/entities/dashboard_entity.dart';
import '../providers/dashboard_provider.dart';
import '../providers/dashboard_state.dart';
import '../widgets/home_derslerim_card.dart';
import '../widgets/home_glass_greeting.dart';
import '../widgets/home_hedeflerim_card.dart';
import '../widgets/home_start_hero.dart';
import '../widgets/home_testler_card.dart';
import '../widgets/notification_bell.dart';

/// Bugün — Glass / Floating Home (D reference). No hero photo.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardState = ref.watch(dashboardProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        title: const SizedBox.shrink(),
        actions: const [
          NotificationBell(),
          SizedBox(width: AppSpacing.xs),
        ],
      ),
      body: StudyGlassAtmosphere(
        child: SafeArea(
          top: false,
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 280),
            child: KeyedSubtree(
              key: ValueKey<String>(switch (dashboardState) {
                DashboardInitial() || DashboardLoading() => 'loading',
                DashboardLoaded() => 'loaded',
                DashboardError() => 'error',
              }),
              child: switch (dashboardState) {
                DashboardInitial() || DashboardLoading() =>
                  const _TodayLoadingView(),
                DashboardLoaded(:final dashboard) =>
                  _TodayLoadedView(dashboard: dashboard),
                DashboardError(:final message) =>
                  _TodayErrorView(message: message),
              },
            ),
          ),
        ),
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 0),
    );
  }
}

class _TodayLoadingView extends StatelessWidget {
  const _TodayLoadingView();

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: EditorialPage.maxContentWidth(width),
        ),
        child: ListView(
          padding: EdgeInsets.only(
            left: EditorialPage.horizontalPadding(width).left,
            right: EditorialPage.horizontalPadding(width).right,
            top: AppSpacing.sm,
            bottom: AppSpacing.xxl,
          ),
          children: const [
            SkeletonCard(height: 72),
            SizedBox(height: AppSpacing.lg),
            SkeletonCard(height: 56),
            SizedBox(height: AppSpacing.md),
            SkeletonCard(height: 72),
            SizedBox(height: AppSpacing.xl),
            SkeletonCard(height: 220),
            SizedBox(height: AppSpacing.lg),
            SkeletonCard(height: 200),
          ],
        ),
      ),
    );
  }
}

class _TodayErrorView extends ConsumerWidget {
  const _TodayErrorView({required this.message});

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
  const _TodayLoadedView({required this.dashboard});

  final DashboardEntity dashboard;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => dashboard.firstName,
    };

    final width = MediaQuery.sizeOf(context).width;
    final hPad = EditorialPage.horizontalPadding(width);

    return RefreshIndicator(
      onRefresh: () => ref.read(dashboardProvider.notifier).retry(),
      child: Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxWidth: EditorialPage.maxContentWidth(width),
          ),
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: EdgeInsets.only(
              left: hPad.left,
              right: hPad.right,
              top: AppSpacing.xs,
              bottom: AppSpacing.xxl,
            ),
            children: [
              HomeGlassGreeting(
                firstName: name,
                onAvatarTap: () => context.push('/profile'),
              ),
              const SizedBox(height: AppSpacing.lg),
              HomeStartHero(
                dashboard: dashboard,
                action: dashboard.nextAction,
              ),
              const SizedBox(height: AppSpacing.section),
              HomeDerslerimCard(dashboard: dashboard),
              const SizedBox(height: AppSpacing.lg),
              HomeTestlerCard(dashboard: dashboard),
              const SizedBox(height: AppSpacing.lg),
              HomeHedeflerimCard(dashboard: dashboard),
              const SizedBox(height: AppSpacing.lg),
              const LiveStudySessionCard(),
            ],
          ),
        ),
      ),
    );
  }
}
