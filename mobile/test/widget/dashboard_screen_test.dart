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
    ],
  );

  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        dashboardRepositoryProvider.overrideWithValue(repository),
        widgetServiceProvider.overrideWithValue(NoOpWidgetService()),
        platformServiceProvider.overrideWithValue(_FakePlatformService()),
        learningProfileProvider.overrideWith((ref) async => _sampleProfile),
      ],
      child: MaterialApp.router(routerConfig: router),
    ),
  );
}

void main() {
  testWidgets('Today yüklenirken skeleton gösterir', (tester) async {
    await _pumpToday(
      tester,
      _FakeDashboardRepository(
        entity: _sampleDashboard,
        delay: const Duration(milliseconds: 200),
      ),
    );

    expect(find.text('Şimdi yap'), findsNothing);
    await tester.pump(const Duration(milliseconds: 250));
  });

  testWidgets('Today tek Primary Action gösterir; hub kartları yoktur', (
    tester,
  ) async {
    await _pumpToday(tester, _FakeDashboardRepository(entity: _sampleDashboard));
    await tester.pump();
    await tester.pump();

    expect(find.text('Şimdi yap'), findsOneWidget);
    expect(find.text('Bu konu üzerinde çalış'), findsOneWidget);
    expect(find.text('Problemler · 25 dk'), findsOneWidget);
    expect(find.text('Başla'), findsOneWidget);
    expect(find.widgetWithText(FilledButton, 'Başla'), findsOneWidget);

    expect(find.textContaining('2 çalışma bloğun kaldı'), findsOneWidget);
    expect(find.textContaining('1 tekrar bekliyor'), findsOneWidget);
    expect(find.textContaining('YKS'), findsWidgets);
    expect(find.textContaining('45 / 120 dk'), findsOneWidget);

    // Demoted Journey Hub / modül kartları
    expect(find.text('Bugünkü görevler'), findsNothing);
    expect(find.text('AI Coach'), findsNothing);
    expect(find.text('Dersler'), findsNothing);
    expect(find.text('Tüm Dersler'), findsNothing);
    expect(find.text('Hızlı İşlemler'), findsNothing);
    expect(find.text('Sistem Entegrasyonu'), findsNothing);
  });

  testWidgets('Bottom navigation Today etiketini gösterir', (tester) async {
    await _pumpToday(tester, _FakeDashboardRepository(entity: _sampleDashboard));
    await tester.pump();
    await tester.pump();

    final navBar = find.byType(NavigationBar);
    expect(navBar, findsOneWidget);
    for (final label in ['Today', 'Plan', 'Pomodoro', 'İstatistik', 'Profil']) {
      expect(
        find.descendant(of: navBar, matching: find.text(label)),
        findsOneWidget,
      );
    }
  });

  testWidgets('API hatasında Tekrar Dene çalışır', (tester) async {
    final repository = _FakeDashboardRepository(
      error: Exception('sunucu hatası'),
      delay: const Duration(milliseconds: 50),
    );
    await _pumpToday(tester, repository);
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Today yüklenemedi'), findsOneWidget);
    expect(find.text('Tekrar Dene'), findsOneWidget);
    expect(repository.callCount, 1);

    await tester.tap(find.text('Tekrar Dene'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Today yüklenemedi'), findsOneWidget);
    expect(repository.callCount, 2);
  });
}
