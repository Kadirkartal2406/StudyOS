import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/study_plan/data/datasources/study_plan_remote_datasource.dart';
import 'package:studyos_mobile/features/study_plan/data/models/study_plan_model.dart';
import 'package:studyos_mobile/features/study_plan/data/repositories/study_plan_repository_impl.dart';
import 'package:studyos_mobile/features/study_plan/domain/entities/study_time.dart';

class _MockStudyPlanRemoteDatasource extends Mock
    implements StudyPlanRemoteDatasource {}

StudyPlanModel _model({String id = 'plan-1', int orderIndex = 0}) {
  return StudyPlanModel(
    id: id,
    userId: 'user-1',
    title: 'Matematik Çalışması',
    subject: 'Matematik',
    topic: 'Türev',
    targetQuestionCount: 20,
    estimatedMinutes: 60,
    status: 'planned',
    completedQuestionCount: 0,
    completedMinutes: 0,
    orderIndex: orderIndex,
    studyDate: DateTime(2026, 7, 16),
    createdAt: DateTime(2026, 7, 16, 8),
    updatedAt: DateTime(2026, 7, 16, 8),
  );
}

void main() {
  late _MockStudyPlanRemoteDatasource datasource;
  late StudyPlanRepositoryImpl repository;

  setUpAll(() {
    registerFallbackValue(<String, dynamic>{});
  });

  setUp(() {
    datasource = _MockStudyPlanRemoteDatasource();
    repository = StudyPlanRepositoryImpl(datasource);
  });

  test('getPlans datasource\'tan gelen modelleri entity listesine dönüştürür',
      () async {
    when(() => datasource.getPlans(any())).thenAnswer(
      (_) async => [_model(id: 'a'), _model(id: 'b', orderIndex: 1)],
    );

    final entities = await repository.getPlans(DateTime(2026, 7, 16));

    expect(entities, hasLength(2));
    expect(entities.first.id, 'a');
    expect(entities.last.orderIndex, 1);
  });

  test('createPlan body\'i doğru inşa eder ve entity döner', () async {
    when(() => datasource.createPlan(any())).thenAnswer((_) async => _model());

    final entity = await repository.createPlan(
      title: 'Matematik Çalışması',
      subject: 'Matematik',
      topic: 'Türev',
      targetQuestionCount: 20,
      estimatedMinutes: 60,
      studyDate: DateTime(2026, 7, 16),
      plannedStartTime: const StudyTime(hour: 9, minute: 0),
      plannedEndTime: const StudyTime(hour: 10, minute: 0),
    );

    expect(entity.title, 'Matematik Çalışması');
    final captured = verify(() => datasource.createPlan(captureAny()))
        .captured
        .single as Map<String, dynamic>;
    expect(captured['title'], 'Matematik Çalışması');
    expect(captured['study_date'], '2026-07-16');
    expect(captured['planned_start_time'], '09:00:00');
    expect(captured['planned_end_time'], '10:00:00');
  });

  test('createPlan saat aralığı verilmediğinde body\'e eklemez', () async {
    when(() => datasource.createPlan(any())).thenAnswer((_) async => _model());

    await repository.createPlan(
      title: 'Fizik',
      subject: 'Fizik',
      targetQuestionCount: 10,
      estimatedMinutes: 30,
      studyDate: DateTime(2026, 7, 16),
    );

    final captured = verify(() => datasource.createPlan(captureAny()))
        .captured
        .single as Map<String, dynamic>;
    expect(captured.containsKey('planned_start_time'), isFalse);
    expect(captured.containsKey('topic'), isFalse);
  });

  test('deletePlan datasource\'u çağırır', () async {
    when(() => datasource.deletePlan(any())).thenAnswer((_) async {});

    await repository.deletePlan('plan-1');

    verify(() => datasource.deletePlan('plan-1')).called(1);
  });

  test('startPlan/completePlan/skipPlan entity döner', () async {
    when(() => datasource.startPlan(any())).thenAnswer((_) async => _model());
    when(
      () => datasource.completePlan(
        any(),
        completedQuestionCount: any(named: 'completedQuestionCount'),
        completedMinutes: any(named: 'completedMinutes'),
      ),
    ).thenAnswer((_) async => _model());
    when(() => datasource.skipPlan(any())).thenAnswer((_) async => _model());

    final started = await repository.startPlan('plan-1');
    final completed =
        await repository.completePlan('plan-1', completedMinutes: 30);
    final skipped = await repository.skipPlan('plan-1');

    expect(started.id, 'plan-1');
    expect(completed.id, 'plan-1');
    expect(skipped.id, 'plan-1');
  });

  test('datasource hata fırlattığında repository de fırlatır', () async {
    when(() => datasource.getPlans(any())).thenThrow(Exception('ağ hatası'));

    expect(() => repository.getPlans(DateTime(2026, 7, 16)), throwsException);
  });
}
