import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/core/errors/app_exception.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_plan_entity.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_plan_status.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_time.dart';
import 'package:studyos_mobile/features/study_plan/domain/repositories/study_plan_repository.dart';
import 'package:studyos_mobile/features/study_plan/presentation/providers/study_plan_provider.dart';
import 'package:studyos_mobile/features/study_plan/presentation/providers/study_plan_state.dart';

class _FakeStudyPlanRepository implements StudyPlanRepository {
  final List<StudyPlanEntity> plans = [];
  int _idCounter = 0;
  AppException? nextError;

  void _maybeThrow() {
    if (nextError != null) {
      final error = nextError!;
      nextError = null;
      throw error;
    }
  }

  bool _isSameDay(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  StudyPlanEntity _find(String id) => plans.firstWhere((p) => p.id == id);

  @override
  Future<List<StudyPlanEntity>> getPlans(DateTime studyDate) async {
    _maybeThrow();
    final result = plans
        .where((p) => _isSameDay(p.studyDate, studyDate))
        .toList()
      ..sort((a, b) => a.orderIndex.compareTo(b.orderIndex));
    return result;
  }

  @override
  Future<StudyPlanEntity> getPlan(String id) async {
    _maybeThrow();
    return _find(id);
  }

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
  }) async {
    _maybeThrow();
    _idCounter += 1;
    final plan = StudyPlanEntity(
      id: 'plan-$_idCounter',
      userId: 'user-1',
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      plannedStartTime: plannedStartTime,
      plannedEndTime: plannedEndTime,
      status: StudyPlanStatus.planned,
      completedQuestionCount: 0,
      completedMinutes: 0,
      orderIndex: orderIndex ?? plans.length,
      studyDate: studyDate,
      createdAt: DateTime(2026, 7, 16),
      updatedAt: DateTime(2026, 7, 16),
    );
    plans.add(plan);
    return plan;
  }

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
  }) async {
    _maybeThrow();
    final index = plans.indexWhere((p) => p.id == id);
    final existing = plans[index];
    final updated = StudyPlanEntity(
      id: existing.id,
      userId: existing.userId,
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      plannedStartTime: plannedStartTime,
      plannedEndTime: plannedEndTime,
      status: existing.status,
      completedQuestionCount: existing.completedQuestionCount,
      completedMinutes: existing.completedMinutes,
      orderIndex: orderIndex ?? existing.orderIndex,
      studyDate: studyDate,
      createdAt: existing.createdAt,
      updatedAt: existing.updatedAt,
    );
    plans[index] = updated;
    return updated;
  }

  @override
  Future<void> deletePlan(String id) async {
    _maybeThrow();
    plans.removeWhere((p) => p.id == id);
  }

  @override
  Future<StudyPlanEntity> startPlan(String id) async {
    _maybeThrow();
    final index = plans.indexWhere((p) => p.id == id);
    final updated = plans[index].copyWith(status: StudyPlanStatus.inProgress);
    plans[index] = updated;
    return updated;
  }

  @override
  Future<StudyPlanEntity> completePlan(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  }) async {
    _maybeThrow();
    final index = plans.indexWhere((p) => p.id == id);
    final existing = plans[index];
    final updated = existing.copyWith(
      status: StudyPlanStatus.completed,
      completedQuestionCount:
          completedQuestionCount ?? existing.targetQuestionCount,
      completedMinutes: completedMinutes ?? existing.estimatedMinutes,
    );
    plans[index] = updated;
    return updated;
  }

  @override
  Future<StudyPlanEntity> skipPlan(String id) async {
    _maybeThrow();
    final index = plans.indexWhere((p) => p.id == id);
    final updated = plans[index].copyWith(status: StudyPlanStatus.skipped);
    plans[index] = updated;
    return updated;
  }
}

void main() {
  late _FakeStudyPlanRepository repository;
  late ProviderContainer container;

  setUp(() {
    repository = _FakeStudyPlanRepository();
    container = ProviderContainer(
      overrides: [studyPlanRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);
    // Notifier'ı hemen oluştur; constructor'daki ilk load() burada tetiklenir
    // ki testin ilk `await settle()` çağrısı bu isteğin bitmesini gerçekten
    // bekleyebilsin (lazy provider aksi halde load()'u settle()'dan SONRA başlatır).
    container.read(studyPlanProvider);
  });

  Future<void> settle() => Future<void>.delayed(Duration.zero);

  test('başlangıçta bugünün planlarını yükler (boş liste)', () async {
    await settle();

    final state = container.read(studyPlanProvider);
    expect(state, isA<StudyPlanLoaded>());
    expect((state as StudyPlanLoaded).plans, isEmpty);
  });

  test('createPlan yeni planı listeye ekler', () async {
    await settle();
    await container.read(studyPlanProvider.notifier).createPlan(
          title: 'Matematik',
          subject: 'Matematik',
          targetQuestionCount: 10,
          estimatedMinutes: 30,
        );

    final state = container.read(studyPlanProvider) as StudyPlanLoaded;
    expect(state.plans, hasLength(1));
    expect(state.plans.first.title, 'Matematik');
    expect(state.plans.first.status, StudyPlanStatus.planned);
  });

  test('updatePlan mevcut planın alanlarını değiştirir', () async {
    await settle();
    final notifier = container.read(studyPlanProvider.notifier);
    await notifier.createPlan(
      title: 'Matematik',
      subject: 'Matematik',
      targetQuestionCount: 10,
      estimatedMinutes: 30,
    );
    final planId =
        (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first.id;

    await notifier.updatePlan(
      id: planId,
      title: 'Fizik',
      subject: 'Fizik',
      targetQuestionCount: 15,
      estimatedMinutes: 45,
    );

    final state = container.read(studyPlanProvider) as StudyPlanLoaded;
    expect(state.plans.first.title, 'Fizik');
    expect(state.plans.first.estimatedMinutes, 45);
  });

  test('start → complete yaşam döngüsü doğru çalışır', () async {
    await settle();
    final notifier = container.read(studyPlanProvider.notifier);
    await notifier.createPlan(
      title: 'Matematik',
      subject: 'Matematik',
      targetQuestionCount: 10,
      estimatedMinutes: 30,
    );
    final planId =
        (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first.id;

    await notifier.startPlan(planId);
    expect(
      (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first.status,
      StudyPlanStatus.inProgress,
    );

    await notifier.completePlan(
      planId,
      completedMinutes: 25,
      completedQuestionCount: 8,
    );
    final completed =
        (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first;
    expect(completed.status, StudyPlanStatus.completed);
    expect(completed.completedMinutes, 25);
    expect(completed.completedQuestionCount, 8);
  });

  test('skipPlan planı atlandı durumuna geçirir', () async {
    await settle();
    final notifier = container.read(studyPlanProvider.notifier);
    await notifier.createPlan(
      title: 'Kimya',
      subject: 'Kimya',
      targetQuestionCount: 5,
      estimatedMinutes: 20,
    );
    final planId =
        (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first.id;

    await notifier.skipPlan(planId);

    expect(
      (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first.status,
      StudyPlanStatus.skipped,
    );
  });

  test('deletePlan planı listeden kaldırır', () async {
    await settle();
    final notifier = container.read(studyPlanProvider.notifier);
    await notifier.createPlan(
      title: 'Silinecek Plan',
      subject: 'Biyoloji',
      targetQuestionCount: 5,
      estimatedMinutes: 20,
    );
    final planId =
        (container.read(studyPlanProvider) as StudyPlanLoaded).plans.first.id;

    await notifier.deletePlan(planId);

    expect(
      (container.read(studyPlanProvider) as StudyPlanLoaded).plans,
      isEmpty,
    );
  });

  test('reorder sürükle-bırak sonrası order_index değerlerini günceller',
      () async {
    await settle();
    final notifier = container.read(studyPlanProvider.notifier);
    await notifier.createPlan(
      title: 'A',
      subject: 'A',
      targetQuestionCount: 1,
      estimatedMinutes: 10,
    );
    await notifier.createPlan(
      title: 'B',
      subject: 'B',
      targetQuestionCount: 1,
      estimatedMinutes: 10,
    );
    await notifier.createPlan(
      title: 'C',
      subject: 'C',
      targetQuestionCount: 1,
      estimatedMinutes: 10,
    );

    // ReorderableListView sözleşmesi: A'yı (index 0) listenin en sonuna
    // taşımak için newIndex = length (3) verilir.
    await notifier.reorder(0, 3);

    final titles = (container.read(studyPlanProvider) as StudyPlanLoaded)
        .plans
        .map((p) => p.title)
        .toList();
    expect(titles, ['B', 'C', 'A']);
  });

  test('changeDate ve goToToday farklı günlerin planlarını getirir', () async {
    await settle();
    final notifier = container.read(studyPlanProvider.notifier);
    final tomorrow = DateTime.now().add(const Duration(days: 1));

    await notifier.createPlan(
      title: 'Bugünkü Plan',
      subject: 'Matematik',
      targetQuestionCount: 5,
      estimatedMinutes: 20,
    );

    await notifier.changeDate(tomorrow);
    expect(
      (container.read(studyPlanProvider) as StudyPlanLoaded).plans,
      isEmpty,
    );

    await notifier.goToToday();
    expect(
      (container.read(studyPlanProvider) as StudyPlanLoaded).plans,
      hasLength(1),
    );
  });

  test('repository hata fırlattığında StudyPlanError durumuna geçer', () async {
    await settle();
    repository.nextError = const NetworkException(message: 'ağ hatası');

    await container.read(studyPlanProvider.notifier).retry();
    await settle();

    final state = container.read(studyPlanProvider);
    expect(state, isA<StudyPlanError>());
    expect((state as StudyPlanError).message, 'ağ hatası');
  });
}
