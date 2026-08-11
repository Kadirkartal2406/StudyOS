import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:studyos_mobile/core/theme/app_theme.dart';
import 'package:studyos_mobile/features/dashboard/domain/entities/dashboard_entity.dart';
import 'package:studyos_mobile/features/dashboard/domain/repositories/dashboard_repository.dart';
import 'package:studyos_mobile/features/dashboard/presentation/providers/dashboard_provider.dart';
import 'package:studyos_mobile/features/dashboard/presentation/screens/dashboard_screen.dart';
import 'package:studyos_mobile/features/dashboard/presentation/screens/menu_screen.dart';
import 'package:studyos_mobile/features/onboarding/domain/entities/learning_profile_entity.dart';
import 'package:studyos_mobile/features/onboarding/presentation/providers/learning_profile_provider.dart';
import 'package:studyos_mobile/features/onboarding/presentation/screens/settings_screen.dart';
import 'package:studyos_mobile/features/study_session/presentation/widgets/today_summary_card.dart';
import 'package:studyos_mobile/core/platform/platform_providers.dart';
import 'package:studyos_mobile/core/platform/widget_service.dart';

class _FakeDashRepo implements DashboardRepository {
  @override
  Future<DashboardEntity> getDashboard() async => const DashboardEntity(
        firstName: 'Kadir',
        dailyStudyGoalMinutes: 120,
        todayStudyMinutes: 68,
        todayQuestionsSolved: 48,
        dailyProgressPercentage: 68,
        todayPlanCount: 3,
        streakDays: 12,
        mySubjectNames: ['Matematik', 'Türkçe', 'Geometri'],
        mySubjectCodes: ['tyt_mat', 'tyt_tur', 'tyt_geo'],
        activeExamType: 'yks',
        nextAction: NextActionEntity(
          title: 'Fonksiyonlar',
          reason: 'Sıradaki blok',
          actionType: 'study_plan',
          deepLinkHint: '/subjects',
          ctaLabel: 'Başla',
        ),
      );
}

Future<void> _pump(
  WidgetTester tester,
  Widget home, {
  ThemeData? theme,
}) async {
  tester.view.physicalSize = const Size(390, 844);
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (_, __) => home),
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
      GoRoute(path: '/menu', builder: (_, __) => const Scaffold()),
      GoRoute(
        path: '/assessment/daily/history',
        builder: (_, __) => const Scaffold(),
      ),
      GoRoute(
        path: '/assessment/daily/start',
        builder: (_, __) => const Scaffold(),
      ),
      GoRoute(path: '/assessment', builder: (_, __) => const Scaffold()),
      GoRoute(path: '/revisions', builder: (_, __) => const Scaffold()),
      GoRoute(path: '/journey', builder: (_, __) => const Scaffold()),
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
        studySessionTodaySummaryProvider.overrideWith(
          (ref) async => <String, dynamic>{
            'focus_minutes': 68,
            'break_minutes': 5,
            'planned_minutes': 120,
            'plan_adherence_pct': 68,
            'goal_gap_minutes': 52,
            'by_subject': <Map<String, dynamic>>[],
          },
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
        theme: theme ?? AppTheme.lightTheme(),
        darkTheme: AppTheme.darkTheme(),
        routerConfig: router,
      ),
    ),
  );
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 400));
}

void main() {
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  testWidgets('golden home light', (tester) async {
    await _pump(tester, const DashboardScreen());
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('goldens/home_light.png'),
    );
  }, tags: ['golden']);

  testWidgets('golden menu light', (tester) async {
    await _pump(tester, const MenuScreen());
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('goldens/menu_light.png'),
    );
  }, tags: ['golden']);

  testWidgets('golden menu dark', (tester) async {
    await _pump(tester, const MenuScreen(), theme: AppTheme.darkTheme());
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('goldens/menu_dark.png'),
    );
  }, tags: ['golden']);

  testWidgets('golden settings light', (tester) async {
    await _pump(tester, const SettingsScreen());
    await expectLater(
      find.byType(MaterialApp),
      matchesGoldenFile('goldens/settings_light.png'),
    );
  }, tags: ['golden']);
}
