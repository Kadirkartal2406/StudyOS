import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/core/errors/app_exception.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_plan_entity.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_plan_status.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_time.dart';
import 'package:studyos_mobile/features/study_plan/domain/repositories/study_plan_repository.dart';
import 'package:studyos_mobile/features/study_plan/presentation/providers/study_plan_provider.dart';
import 'package:studyos_mobile/features/study_plan/presentation/screens/study_plan_screen.dart';

StudyPlanEntity _plan({
  String id = 'plan-1',
  String title = 'Matematik Çalışması',
  StudyPlanStatus status = StudyPlanStatus.planned,
  int orderIndex = 0,
  StudyTime? plannedStartTime,
  StudyTime? plannedEndTime,
}) {
  return StudyPlanEntity(
    id: id,
    userId: 'user-1',
    title: title,
    subject: 'Matematik',
    topic: 'Türev',
    targetQuestionCount: 20,
    estimatedMinutes: 60,
    plannedStartTime: plannedStartTime,
    plannedEndTime: plannedEndTime,
    status: status,
    completedQuestionCount: 0,
    completedMinutes: 0,
    orderIndex: orderIndex,
    studyDate: DateTime.now(),
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );
}

class _FakeStudyPlanRepository implements StudyPlanRepository {
  _FakeStudyPlanRepository({List<StudyPlanEntity>? initialPlans, this.error})
      : plans = initialPlans ?? [];

  List<StudyPlanEntity> plans;
  final Object? error;
  int getPlansCallCount = 0;

  @override
  Future<List<StudyPlanEntity>> getPlans(DateTime studyDate) async {
    getPlansCallCount++;
    if (error != null) throw error!;
    return plans;
  }

  @override
  Future<StudyPlanEntity> getPlan(String id) async =>
      plans.firstWhere((p) => p.id == id);

  @override
  Future<StudyPlanEntity> createPlan({
    required String title,
    required String subject,
    String? topic,
    required int targetQuestionCount,
    required int estimatedMinutes,
    required DateTime studyDate,
    StudyTime? plannedStartTime,
    StudyTime? plannedEndTime,
    int? orderIndex,
  }) async =>
      throw UnimplementedError();

  @override
  Future<StudyPlanEntity> updatePlan({
    required String id,
    required String title,
    required String subject,
    String? topic,
    required int targetQuestionCount,
    required int estimatedMinutes,
    required DateTime studyDate,
    StudyTime? plannedStartTime,
    StudyTime? plannedEndTime,
    int? orderIndex,
  }) async =>
      throw UnimplementedError();

  @override
  Future<void> deletePlan(String id) async {
    plans = plans.where((p) => p.id != id).toList();
  }

  @override
  Future<StudyPlanEntity> startPlan(String id) async {
    final index = plans.indexWhere((p) => p.id == id);
    final updated = plans[index].copyWith(status: StudyPlanStatus.inProgress);
    plans = [...plans]..[index] = updated;
    return updated;
  }

  @override
  Future<StudyPlanEntity> completePlan(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  }) async {
    final index = plans.indexWhere((p) => p.id == id);
    final updated = plans[index].copyWith(status: StudyPlanStatus.completed);
    plans = [...plans]..[index] = updated;
    return updated;
  }

  @override
  Future<StudyPlanEntity> skipPlan(String id) async {
    final index = plans.indexWhere((p) => p.id == id);
    final updated = plans[index].copyWith(status: StudyPlanStatus.skipped);
    plans = [...plans]..[index] = updated;
    return updated;
  }
}

Future<void> _pumpScreen(
  WidgetTester tester,
  StudyPlanRepository repository,
) async {
  tester.view.physicalSize = const Size(800, 2400);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);

  final router = GoRouter(
    initialLocation: '/study-plan',
    routes: [
      GoRoute(
        path: '/',
        builder: (_, __) => const Scaffold(body: Text('today')),
      ),
      GoRoute(
        path: '/study-plan',
        builder: (_, __) => const StudyPlanScreen(),
      ),
    ],
  );

  await tester.pumpWidget(
    ProviderScope(
      overrides: [studyPlanRepositoryProvider.overrideWithValue(repository)],
      child: MaterialApp.router(routerConfig: router),
    ),
  );
}

void main() {
  testWidgets('Yüklenirken CircularProgressIndicator gösterir', (tester) async {
    await _pumpScreen(tester, _FakeStudyPlanRepository());

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('AS-4: boş durumda Plan Ekle yok; Today CTA var', (tester) async {
    await _pumpScreen(tester, _FakeStudyPlanRepository());
    await tester.pump();
    await tester.pump();

    expect(find.text('Bugün için blok yok'), findsOneWidget);
    expect(find.text('Plan Ekle'), findsNothing);
    expect(find.byType(FloatingActionButton), findsNothing);
    expect(find.text("Today'e git"), findsOneWidget);
  });

  testWidgets('AS-4: FAB yok; Complete/Skip primary; reorder yok', (tester) async {
    final repository = _FakeStudyPlanRepository(
      initialPlans: [
        _plan(id: 'a', title: 'Matematik'),
        _plan(id: 'b', title: 'Fizik', orderIndex: 1),
      ],
    );
    await _pumpScreen(tester, repository);
    await tester.pump();
    await tester.pump();

    expect(find.text('Bugünkü bloklar'), findsOneWidget);
    expect(find.byType(FloatingActionButton), findsNothing);
    expect(find.byType(ReorderableListView), findsNothing);
    expect(find.text('Tamamla'), findsWidgets);
    expect(find.text('Atla'), findsWidgets);
    expect(find.text('Matematik · Türev'), findsWidgets);
    expect(find.text('Günlük İlerleme'), findsOneWidget);
  });

  testWidgets('Başlat secondary; Atla primary çalışır', (tester) async {
    final repository = _FakeStudyPlanRepository(initialPlans: [_plan()]);
    await _pumpScreen(tester, repository);
    await tester.pump();
    await tester.pump();

    expect(find.text('Bekliyor'), findsOneWidget);

    await tester.tap(find.text('Atla'));
    await tester.pump();
    await tester.pump();

    expect(find.text('Atlandı'), findsOneWidget);
  });

  testWidgets('Tamamla primary çalışır', (tester) async {
    final repository = _FakeStudyPlanRepository(initialPlans: [_plan()]);
    await _pumpScreen(tester, repository);
    await tester.pump();
    await tester.pump();

    await tester.tap(find.text('Tamamla'));
    await tester.pump();
    await tester.pump();

    expect(find.text('Tamamlandı'), findsOneWidget);
  });

  testWidgets('API hatasında Tekrar Dene butonu gösterir ve tekrar dener',
      (tester) async {
    final repository = _FakeStudyPlanRepository(
      error: const NetworkException(message: 'sunucu hatası'),
    );
    await _pumpScreen(tester, repository);
    await tester.pump();
    await tester.pump();

    expect(find.text('Bloklar yüklenemedi'), findsOneWidget);
    expect(find.text('Tekrar Dene'), findsOneWidget);
    expect(repository.getPlansCallCount, 1);

    await tester.tap(find.text('Tekrar Dene'));
    await tester.pump();
    await tester.pump();

    expect(repository.getPlansCallCount, 2);
  });

  testWidgets('Bottom navigation Plan sekmesi aktif olarak işaretlenir',
      (tester) async {
    await _pumpScreen(tester, _FakeStudyPlanRepository());
    await tester.pump();
    await tester.pump();

    final navBar = tester.widget<NavigationBar>(find.byType(NavigationBar));
    expect(navBar.selectedIndex, 1);
  });
}
