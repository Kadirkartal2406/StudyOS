import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/adaptive_planner/data/datasources/planner_remote_datasource.dart';
import 'package:studyos_mobile/features/adaptive_planner/data/repositories/planner_repository.dart';
import 'package:studyos_mobile/features/adaptive_planner/domain/entities/planner_entity.dart';

class _MockRemote extends Mock implements PlannerRemoteDatasource {}

PlannerDraftEntity _sampleDraft() {
  return PlannerDraftEntity(
    id: '11111111-1111-1111-1111-111111111111',
    status: 'draft',
    targetExam: 'tyt',
    targetNet: 90,
    availableDays: const [0, 2],
    availableHours: 2,
    items: [
      PlannerItemEntity(
        studyDate: DateTime.parse('2026-07-20'),
        title: 'Matematik blok',
        subject: 'Matematik',
        targetQuestionCount: 20,
        estimatedMinutes: 60,
        reason: 'Düşük doğruluk oranı',
      ),
    ],
    overviewReason: 'Zayıf derslere odaklan',
  );
}

void main() {
  late _MockRemote remote;
  late PlannerRepository repo;

  setUpAll(() {
    registerFallbackValue(<String, dynamic>{});
  });

  setUp(() {
    remote = _MockRemote();
    repo = PlannerRepository(remote);
  });

  test('generate remote body ile çağırır ve draft döner', () async {
    final draft = _sampleDraft();
    when(
      () => remote.generate(any()),
    ).thenAnswer((_) async => draft);

    final result = await repo.generate(
      targetExam: 'tyt',
      targetNet: 90,
      availableDays: const [0, 2],
      availableHours: 2,
    );

    expect(result.id, draft.id);
    expect(result.items.first.reason, 'Düşük doğruluk oranı');
    verify(
      () => remote.generate({
        'target_exam': 'tyt',
        'target_net': 90.0,
        'available_days': [0, 2],
        'available_hours': 2.0,
      }),
    ).called(1);
  });

  test('accept force bayrağını iletir', () async {
    final draft = _sampleDraft();
    when(
      () => remote.accept(any(), force: any(named: 'force')),
    ).thenAnswer((_) async => draft);

    await repo.accept(draft.id, force: true);

    verify(() => remote.accept(draft.id, force: true)).called(1);
  });

  test('explain explanation döner', () async {
    when(() => remote.explain(any())).thenAnswer(
      (_) async => const PlannerExplainEntity(
        draftId: '11111111-1111-1111-1111-111111111111',
        explanation: 'Çünkü zayıf derslerin var',
        provider: 'null',
        usedFallback: true,
      ),
    );

    final result = await repo.explain('11111111-1111-1111-1111-111111111111');
    expect(result.explanation, contains('zayıf'));
  });
}
