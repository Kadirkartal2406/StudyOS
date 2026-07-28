import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:studyos_mobile/features/study_session/data/datasources/study_session_remote_datasource.dart';
import 'package:studyos_mobile/features/study_session/data/models/study_session_model.dart';
import 'package:studyos_mobile/features/study_session/data/repositories/study_session_repository_impl.dart';
import 'package:studyos_mobile/features/study_session/domain/entities/study_session_status.dart';

class _MockRemote extends Mock implements StudySessionRemoteDatasource {}

StudySessionModel _model({String status = 'running'}) {
  return StudySessionModel(
    id: '11111111-1111-1111-1111-111111111111',
    userId: '22222222-2222-2222-2222-222222222222',
    startedAt: DateTime.parse('2026-07-16T10:00:00Z'),
    plannedDurationMinutes: 25,
    actualDurationMinutes: 0,
    breakDurationMinutes: 5,
    completedQuestions: 0,
    completedTopics: 0,
    status: status,
    createdAt: DateTime.parse('2026-07-16T10:00:00Z'),
    updatedAt: DateTime.parse('2026-07-16T10:00:00Z'),
  );
}

void main() {
  late _MockRemote remote;
  late StudySessionRepositoryImpl repository;

  setUp(() {
    remote = _MockRemote();
    repository = StudySessionRepositoryImpl(remote);
  });

  test('start builds body and returns entity', () async {
    when(() => remote.start(any())).thenAnswer((_) async => _model());

    final entity = await repository.start(
      plannedDurationMinutes: 25,
      breakDurationMinutes: 5,
      studyPlanId: 'plan-1',
    );

    expect(entity.status, StudySessionStatus.running);
    final captured = verify(() => remote.start(captureAny())).captured.single
        as Map<String, dynamic>;
    expect(captured['planned_duration_minutes'], 25);
    expect(captured['break_duration_minutes'], 5);
    expect(captured['study_plan_id'], 'plan-1');
  });

  test('pause and resume delegate to remote', () async {
    when(() => remote.pause())
        .thenAnswer((_) async => _model(status: 'paused'));
    when(() => remote.resume())
        .thenAnswer((_) async => _model(status: 'running'));

    expect((await repository.pause()).status, StudySessionStatus.paused);
    expect((await repository.resume()).status, StudySessionStatus.running);
  });

  test('finish sends optional question fields', () async {
    when(() => remote.finish(any()))
        .thenAnswer((_) async => _model(status: 'completed'));

    final entity = await repository.finish(completedQuestions: 8);

    expect(entity.status, StudySessionStatus.completed);
    final body = verify(() => remote.finish(captureAny())).captured.single
        as Map<String, dynamic>;
    expect(body['completed_questions'], 8);
  });

  test('getToday maps list', () async {
    when(() => remote.getToday()).thenAnswer((_) async => [_model()]);

    final list = await repository.getToday();

    expect(list, hasLength(1));
    expect(list.first.plannedDurationMinutes, 25);
  });
}
