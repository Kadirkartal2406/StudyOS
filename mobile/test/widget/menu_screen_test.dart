import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/core/theme/app_theme.dart';
import 'package:studyos_mobile/features/dashboard/domain/entities/dashboard_entity.dart';
import 'package:studyos_mobile/features/dashboard/domain/repositories/dashboard_repository.dart';
import 'package:studyos_mobile/features/dashboard/presentation/providers/dashboard_provider.dart';
import 'package:studyos_mobile/features/dashboard/presentation/screens/menu_screen.dart';
import 'package:studyos_mobile/features/onboarding/domain/entities/learning_profile_entity.dart';
import 'package:studyos_mobile/features/onboarding/presentation/providers/learning_profile_provider.dart';
import 'package:studyos_mobile/core/platform/platform_providers.dart';
import 'package:studyos_mobile/core/platform/widget_service.dart';
import 'package:studyos_mobile/shared/widgets/study_icons.dart';
import 'package:studyos_mobile/shared/widgets/study_liquid_glass.dart';

class _FakeDashRepo implements DashboardRepository {
  @override
  Future<DashboardEntity> getDashboard() async => const DashboardEntity(
        firstName: 'Kadir',
        dailyStudyGoalMinutes: 120,
        todayStudyMinutes: 68,
        todayQuestionsSolved: 8,
        dailyProgressPercentage: 68,
        streakDays: 12,
        activeExamType: 'yks',
      );
}

void main() {
  testWidgets('Menu matches profile mockup structure', (tester) async {
    tester.view.physicalSize = const Size(400, 1800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final router = GoRouter(
      initialLocation: '/menu',
      routes: [
        GoRoute(path: '/menu', builder: (_, __) => const MenuScreen()),
        GoRoute(path: '/profile', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/settings', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/statistics', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/goals', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/exams', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/memory', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/resources', builder: (_, __) => const Scaffold()),
        GoRoute(
          path: '/notification-settings',
          builder: (_, __) => const Scaffold(),
        ),
        GoRoute(path: '/study-plan', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/pomodoro', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/feedback', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/dashboard', builder: (_, __) => const Scaffold()),
        GoRoute(path: '/subjects', builder: (_, __) => const Scaffold()),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dashboardRepositoryProvider.overrideWithValue(_FakeDashRepo()),
          widgetServiceProvider.overrideWithValue(NoOpWidgetService()),
          learningProfileProvider.overrideWith(
            (ref) async => const LearningProfileEntity(
              userId: 'u1',
              journeyStage: 'learning',
              onboardingCompleted: true,
              onboardingSkipped: false,
              onboardingRequired: false,
              dailyStudyMinutes: 120,
              availableDays: [0, 1, 2, 3, 4],
              availableHours: 2.5,
              baselineLevel: 'intermediate',
              primaryExamType: 'yks',
              activeExamType: 'yks',
            ),
          ),
          dashboardProvider.overrideWith((ref) {
            return DashboardNotifier(
              ref.watch(dashboardRepositoryProvider),
              ref.watch(widgetServiceProvider),
              autoLoad: true,
              shouldAutoUpdateWidget: () => false,
            );
          }),
        ],
        child: MaterialApp.router(
          theme: AppTheme.lightTheme(),
          routerConfig: router,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Premium'), findsOneWidget);
    expect(find.text('Günlük Çalışma'), findsOneWidget);
    expect(find.text('Seri'), findsOneWidget);
    expect(find.text('Profilim'), findsOneWidget);
    expect(find.text('Odak Modu'), findsOneWidget);
    expect(find.text('Çıkış Yap'), findsOneWidget);
    expect(find.byIcon(StudyIcons.logout), findsOneWidget);
    expect(find.byType(StudyLiquidGlass), findsWidgets);

    await tester.scrollUntilVisible(
      find.text('Hakkında'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Tema'), findsOneWidget);
    expect(find.text('Dil'), findsOneWidget);
  });
}
