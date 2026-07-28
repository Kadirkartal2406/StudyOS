import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/core/platform/notification_service.dart';
import 'package:studyos_mobile/core/platform/platform_providers.dart';
import 'package:studyos_mobile/features/adaptive_planner/presentation/screens/adaptive_planner_screen.dart';
import 'package:studyos_mobile/features/dashboard/presentation/widgets/planner_summary_card.dart';
import 'package:studyos_mobile/features/onboarding/domain/entities/learning_profile_entity.dart';
import 'package:studyos_mobile/features/onboarding/presentation/providers/learning_profile_provider.dart';

class _NoOpNotifications implements NotificationService {
  @override
  Future<void> init() async {}

  @override
  Future<void> show({
    required AppNotificationType type,
    required String title,
    required String body,
  }) async {}

  @override
  Future<void> schedule({
    required AppNotificationType type,
    required String title,
    required String body,
    required Duration after,
    required int notificationId,
  }) async {}

  @override
  Future<void> cancel(int notificationId) async {}

  @override
  Future<void> cancelAll() async {}

  @override
  Future<String?> getFcmToken() async => null;
}

const _readyProfile = LearningProfileEntity(
  userId: 'u1',
  journeyStage: 'learning',
  onboardingCompleted: true,
  onboardingSkipped: false,
  onboardingRequired: false,
  dailyStudyMinutes: 120,
  availableDays: [0, 2, 4],
  availableHours: 2,
  baselineLevel: 'beginner',
  primaryExamType: 'yks',
  examTargets: [
    ExamTargetEntity(
      id: 't1',
      examType: 'yks',
      isPrimary: true,
      targetNet: 90,
    ),
  ],
  subjects: [
    UserSubjectEntity(
      subjectCode: 'tyt_matematik',
      subjectName: 'Matematik',
      isActive: true,
      section: 'tyt',
    ),
  ],
);

void main() {
  testWidgets('AS-4: profil doluyken Suggest yüzeyi; wizard yok', (tester) async {
    tester.view.physicalSize = const Size(800, 1600);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final router = GoRouter(
      initialLocation: '/planner',
      routes: [
        GoRoute(
          path: '/planner',
          builder: (_, __) => const AdaptivePlannerScreen(),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appNotificationServiceProvider.overrideWithValue(_NoOpNotifications()),
          learningProfileProvider.overrideWith((ref) async => _readyProfile),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Önerilen çalışma planı'), findsOneWidget);
    expect(find.text('Sistem önerisi'), findsOneWidget);
    expect(find.text('Öneriyi göster'), findsOneWidget);
    expect(find.text('AI Plan Oluştur'), findsNothing);
    expect(find.text('Plan Oluştur'), findsNothing);
    expect(find.text('Adım 1 / 4'), findsNothing);
  });

  testWidgets('AS-4: profil eksikse parametre adımları kalır', (tester) async {
    tester.view.physicalSize = const Size(800, 1600);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final router = GoRouter(
      initialLocation: '/planner',
      routes: [
        GoRoute(
          path: '/planner',
          builder: (_, __) => const AdaptivePlannerScreen(),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appNotificationServiceProvider.overrideWithValue(_NoOpNotifications()),
          learningProfileProvider.overrideWith(
            (ref) async => const LearningProfileEntity(
              userId: 'u1',
              journeyStage: 'learning',
              onboardingCompleted: true,
              onboardingSkipped: false,
              onboardingRequired: false,
              dailyStudyMinutes: 120,
              availableDays: [],
              availableHours: 0,
              baselineLevel: 'beginner',
              examTargets: [],
            ),
          ),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('Adım 1 / 4'), findsOneWidget);
    expect(find.text('Hedef sınav ve net'), findsOneWidget);
  });

  testWidgets('PlannerSummaryCard Suggest dili', (tester) async {
    final router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/',
          builder: (_, __) => const Scaffold(
            body: PlannerSummaryCard(),
          ),
        ),
        GoRoute(
          path: '/planner',
          builder: (_, __) => const Scaffold(body: Text('planner')),
        ),
      ],
    );

    await tester.pumpWidget(
      MaterialApp.router(routerConfig: router),
    );

    expect(find.text('Bu hafta öneri yok'), findsOneWidget);
    expect(find.text('Öneriye bak'), findsOneWidget);
    expect(find.text('Oluştur'), findsNothing);
  });

  testWidgets('PlannerSummaryCard overview_reason gösterir', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: PlannerSummaryCard(
            draftId: '11111111-1111-1111-1111-111111111111',
            status: 'draft',
            targetExam: 'tyt',
            targetNet: 90,
            itemCount: 3,
            overviewReason: 'Zayıf derslere öncelik',
          ),
        ),
      ),
    );

    expect(find.text('Önerilen çalışma planı'), findsOneWidget);
    expect(find.textContaining('Zayıf derslere öncelik'), findsOneWidget);
  });
}
