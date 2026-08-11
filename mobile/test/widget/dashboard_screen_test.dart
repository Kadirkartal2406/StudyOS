import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/core/platform/platform_providers.dart';
import 'package:studyos_mobile/core/platform/platform_service.dart';
import 'package:studyos_mobile/core/platform/widget_service.dart';
import 'package:studyos_mobile/features/dashboard/domain/entities/dashboard_entity.dart';
import 'package:studyos_mobile/features/dashboard/domain/repositories/dashboard_repository.dart';
import 'package:studyos_mobile/features/dashboard/presentation/providers/dashboard_provider.dart';
import 'package:studyos_mobile/features/dashboard/presentation/screens/dashboard_screen.dart';
import 'package:studyos_mobile/features/onboarding/domain/entities/learning_profile_entity.dart';
import 'package:studyos_mobile/features/onboarding/presentation/providers/learning_profile_provider.dart';
import 'package:studyos_mobile/features/study_session/presentation/widgets/today_summary_card.dart';
import 'package:studyos_mobile/shared/widgets/app_bottom_nav_bar.dart';
import 'package:studyos_mobile/shared/widgets/study_glass_button.dart';

class _FakeDashboardRepository implements DashboardRepository {
  _FakeDashboardRepository({this.entity, this.error, this.delay = Duration.zero});

  final DashboardEntity? entity;
  final Object? error;
  final Duration delay;

  int callCount = 0;

  @override
  Future<DashboardEntity> getDashboard() async {
    callCount++;
    if (delay > Duration.zero) await Future<void>.delayed(delay);
    if (error != null) throw error!;
    return entity!;
  }
}

class _FakePlatformService implements PlatformService {
  @override
  Future<bool> areNotificationsAllowed() async => true;

  @override
  Future<bool> canScheduleExactAlarms() async => true;

  @override
  Future<void> openSystemNotificationSettings() async {}

  @override
  Future<bool> requestNotificationPermission() async => true;
}

const _sampleDashboard = DashboardEntity(
  firstName: 'Kadir',
  dailyStudyGoalMinutes: 120,
  todayStudyMinutes: 45,
  todayQuestionsSolved: 8,
  dailyProgressPercentage: 37.5,
  todayStudiedTopic: 'Geometri',
  todayPlanCount: 3,
  completedPlanCount: 1,
  todayAiRecommendation: 'Bugün Geometri çalışmanı öneriyorum.',
  todayAiRecommendationCode: 'neglected_subject',
  todayAiRecommendationReason: 'Son 5 gündür tekrar yapılmadı.',
  revisionDueToday: 2,
  revisionNextTitle: 'Türev',
  journeyTodayPct: 40,
  journeyWeekPct: 55,
  journeyMonthPct: 30,
  journeyStage: 'building',
  journeyDaysRemaining: 120,
  mySubjectNames: ['Matematik', 'Türkçe', 'Geometri'],
  mySubjectCodes: ['tyt_matematik', 'tyt_turkce', 'tyt_geometri'],
  activeExamType: 'yks',
  primaryExamType: 'yks',
  primaryTarget: DashboardExamTargetEntity(
    examType: 'yks',
    isPrimary: true,
    targetUniversity: 'ODTÜ',
    targetDepartment: 'Bilgisayar',
    targetNet: 95,
  ),
  nextAction: NextActionEntity(
    title: 'Bu konu üzerinde çalış',
    subtitle: 'Problemler · 25 dk',
    reason: 'Bugünkü sıradaki çalışma bloğun.',
    actionType: 'study_plan',
    deepLinkHint: '/subjects/tyt_matematik/topics/tyt_mat_problemler',
    ctaLabel: 'Başla',
    confidenceTone: 'high',
    purpose: 'study',
    toolHint: 'pomodoro',
  ),
  todayContextLines: [
    'Bugün 2 çalışma bloğun kaldı',
    'Bugün 1 tekrar bekliyor',
  ],
  todayJourneyLine: 'YKS · ODTÜ Bilgisayar · 120 gün kaldı',
);

const _sampleProfile = LearningProfileEntity(
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
  examTargets: [
    ExamTargetEntity(id: 't1', examType: 'yks', isPrimary: true),
    ExamTargetEntity(id: 't2', examType: 'yds', isPrimary: false),
  ],
);

Future<void> _pumpToday(
  WidgetTester tester,
  DashboardRepository repository,
) async {
  tester.view.physicalSize = const Size(800, 2400);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (_, __) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/study-plan',
        builder: (_, __) => const Scaffold(body: Text('study-plan')),
      ),
      GoRoute(
        path: '/subjects/:subjectCode/topics/:topicCode',
        builder: (_, state) => Scaffold(
          body: Text('ws:${state.pathParameters['topicCode']}'),
        ),
      ),
      GoRoute(
        path: '/subjects/:subjectCode',
        builder: (_, state) => Scaffold(
          body: Text('subject:${state.pathParameters['subjectCode']}'),
        ),
      ),
      GoRoute(
        path: '/pomodoro',
        builder: (_, __) => const Scaffold(body: Text('pomodoro')),
      ),
      GoRoute(
        path: '/revisions',
        builder: (_, __) => const Scaffold(body: Text('revisions')),
      ),
      GoRoute(
        path: '/notification-settings',
        builder: (_, __) => const Scaffold(body: Text('settings')),
      ),
      GoRoute(
        path: '/profile',
        builder: (_, __) => const Scaffold(body: Text('profile')),
      ),
      GoRoute(
        path: '/journey',
        builder: (_, __) => const Scaffold(body: Text('journey')),
      ),
      GoRoute(
        path: '/assessment',
        builder: (_, __) => const Scaffold(body: Text('assessment')),
      ),
      GoRoute(
        path: '/assessment/daily/history',
        builder: (_, __) => const Scaffold(body: Text('daily-history')),
      ),
      GoRoute(
        path: '/assessment/daily/start',
        builder: (_, __) => const Scaffold(body: Text('daily-start')),
      ),
      GoRoute(
        path: '/dashboard',
        builder: (_, __) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/subjects',
        builder: (_, __) => const Scaffold(body: Text('subjects')),
      ),
      GoRoute(
        path: '/menu',
        builder: (_, __) => const Scaffold(body: Text('menu')),
      ),
    ],
  );

  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        dashboardRepositoryProvider.overrideWithValue(repository),
        widgetServiceProvider.overrideWithValue(NoOpWidgetService()),
        platformServiceProvider.overrideWithValue(_FakePlatformService()),
        learningProfileProvider.overrideWith((ref) async => _sampleProfile),
        studySessionTodaySummaryProvider.overrideWith(
          (ref) async => <String, dynamic>{
            'focus_minutes': 45,
            'break_minutes': 5,
            'planned_minutes': 120,
            'plan_adherence_pct': 37.5,
            'goal_gap_minutes': 75,
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
      child: MaterialApp.router(routerConfig: router),
    ),
  );
}

void main() {
  testWidgets('Bugün yüklenirken skeleton gösterir', (tester) async {
    await _pumpToday(
      tester,
      _FakeDashboardRepository(
        entity: _sampleDashboard,
        delay: const Duration(milliseconds: 200),
      ),
    );

    expect(find.text('Çalışmaya Başla'), findsNothing);
    await tester.pump(const Duration(milliseconds: 250));
  });

  testWidgets('Glass Home: greeting, CTA, sections match D reference', (
    tester,
  ) async {
    await _pumpToday(tester, _FakeDashboardRepository(entity: _sampleDashboard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));
    await tester.pump(const Duration(milliseconds: 50));

    expect(find.text('Merhaba,'), findsOneWidget);
    expect(find.text('Kadir 👋'), findsOneWidget);
    expect(find.text('Bugün ne çalışacaksın?'), findsOneWidget);
    expect(find.text('Çalışmaya Başla'), findsOneWidget);
    expect(find.text('Planlanan'), findsOneWidget);
    expect(find.text('3 Ders'), findsOneWidget);
    expect(find.text('İlerleme'), findsOneWidget);
    expect(find.text('Süre'), findsOneWidget);

    expect(find.text('Derslerim'), findsWidgets);
    expect(find.text('Derse Devam Et'), findsOneWidget);
    expect(find.text('Matematik'), findsOneWidget);

    expect(find.text('Testler'), findsOneWidget);
    expect(find.text('Teste Başla'), findsOneWidget);
    expect(find.text('Günün Denemesi'), findsOneWidget);

    expect(find.text('Hedeflerim'), findsOneWidget);
    expect(find.text('Hedefleri Gör'), findsOneWidget);
    expect(find.text('Günlük Hedef\nTamamlandı'), findsOneWidget);

    expect(find.byType(StudyGlassButton), findsWidgets);
    expect(find.text('Neden?'), findsOneWidget);

    // Old editorial photo / card-wall remnants must stay gone
    expect(find.text('Şimdi yap'), findsNothing);
    expect(find.text('Bugünkü ilerleme'), findsNothing);
    expect(find.text('Bugünkü görevler'), findsNothing);
    expect(find.text('AI Coach'), findsNothing);
    expect(find.text('Hızlı İşlemler'), findsNothing);
  });

  testWidgets('Bottom navigation Bugün etiketini gösterir', (tester) async {
    await _pumpToday(tester, _FakeDashboardRepository(entity: _sampleDashboard));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));

    final navBar = find.byType(AppBottomNavBar);
    expect(navBar, findsOneWidget);
    for (final label in ['Bugün', 'Derslerim', 'Odak', 'Planım', 'Menü']) {
      expect(
        find.descendant(of: navBar, matching: find.text(label)),
        findsOneWidget,
      );
    }
  });

  testWidgets('API hatasında Tekrar dene çalışır', (tester) async {
    final repository = _FakeDashboardRepository(
      error: Exception('sunucu hatası'),
      delay: const Duration(milliseconds: 50),
    );
    await _pumpToday(tester, repository);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('Bugün yüklenemedi'), findsOneWidget);
    expect(find.text('Tekrar dene'), findsOneWidget);
    expect(repository.callCount, 1);

    await tester.tap(find.text('Tekrar dene'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('Bugün yüklenemedi'), findsOneWidget);
    expect(repository.callCount, 2);
  });
}
