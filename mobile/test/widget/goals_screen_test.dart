import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studyos_mobile/core/platform/notification_service.dart';
import 'package:studyos_mobile/core/platform/platform_providers.dart';
import 'package:studyos_mobile/features/goal_engine/domain/entities/goal_entity.dart';
import 'package:studyos_mobile/features/goal_engine/domain/entities/goal_progress_entity.dart';
import 'package:studyos_mobile/features/goal_engine/domain/repositories/goal_repository.dart';
import 'package:studyos_mobile/features/goal_engine/presentation/providers/goal_provider.dart';
import 'package:studyos_mobile/features/goal_engine/presentation/screens/goals_screen.dart';

class _MockRepo extends Mock implements GoalRepository {}

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

void main() {
  late _MockRepo repo;

  setUp(() {
    repo = _MockRepo();
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('liste boşken boş durum gösterir', (tester) async {
    when(() => repo.listActive()).thenAnswer((_) async => []);
    when(() => repo.getProgress()).thenAnswer(
      (_) async => const GoalProgressEntity(
        items: [],
        activeCount: 0,
        completedCount: 0,
        averageProgress: 0,
      ),
    );

    final router = GoRouter(
      initialLocation: '/goals',
      routes: [
        GoRoute(
          path: '/goals',
          builder: (_, __) => const GoalsScreen(),
        ),
        GoRoute(
          path: '/goals/add',
          builder: (_, __) => const Scaffold(body: Text('add')),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          goalRepositoryProvider.overrideWithValue(repo),
          appNotificationServiceProvider.overrideWithValue(_NoOpNotifications()),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('Hedefler'), findsOneWidget);
    expect(find.text('Henüz hedef yok'), findsOneWidget);
  });

  testWidgets('aktif hedef kartını gösterir', (tester) async {
    final now = DateTime.parse('2026-07-16T10:00:00Z');
    when(() => repo.listActive()).thenAnswer(
      (_) async => [
        GoalEntity(
          id: '11111111-1111-1111-1111-111111111111',
          userId: '22222222-2222-2222-2222-222222222222',
          title: 'Haftalık Fizik',
          goalType: GoalType.subject,
          targetValue: 200,
          currentValue: 80,
          progress: 40,
          priority: GoalPriority.medium,
          period: GoalPeriod.weekly,
          status: GoalStatus.active,
          startDate: now,
          endDate: now.add(const Duration(days: 5)),
          milestonesReached: const [],
          remaining: 120,
          createdAt: now,
          updatedAt: now,
          subject: 'Fizik',
        ),
      ],
    );
    when(() => repo.getProgress()).thenAnswer(
      (_) async => const GoalProgressEntity(
        items: [],
        activeCount: 1,
        completedCount: 0,
        averageProgress: 40,
      ),
    );

    final router = GoRouter(
      initialLocation: '/goals',
      routes: [
        GoRoute(
          path: '/goals',
          builder: (_, __) => const GoalsScreen(),
        ),
        GoRoute(
          path: '/goals/:id',
          builder: (_, __) => const Scaffold(body: Text('detail')),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          goalRepositoryProvider.overrideWithValue(repo),
          appNotificationServiceProvider.overrideWithValue(_NoOpNotifications()),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('Haftalık Fizik'), findsOneWidget);
    expect(find.textContaining('Kalan: 120'), findsOneWidget);
  });
}
