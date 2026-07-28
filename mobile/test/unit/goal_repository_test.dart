import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/goal_engine/data/datasources/goal_remote_datasource.dart';
import 'package:studyos_mobile/features/goal_engine/data/models/goal_models.dart';
import 'package:studyos_mobile/features/goal_engine/data/repositories/goal_repository_impl.dart';

class _MockRemote extends Mock implements GoalRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late GoalRepositoryImpl repo;

  setUpAll(() {
    registerFallbackValue(<String, dynamic>{});
  });

  setUp(() {
    remote = _MockRemote();
    repo = GoalRepositoryImpl(remote);
  });

  final model = GoalModel.fromJson({
    'id': '11111111-1111-1111-1111-111111111111',
    'user_id': '22222222-2222-2222-2222-222222222222',
    'title': 'Soru hedefi',
    'description': null,
    'goal_type': 'question',
    'target_value': 100,
    'current_value': 40,
    'progress': 40,
    'priority': 'medium',
    'period': 'weekly',
    'status': 'active',
    'subject': null,
    'topic': null,
    'start_date': '2026-07-13',
    'end_date': '2026-07-19',
    'completed_at': null,
    'metadata': {},
    'milestones_reached': [],
    'remaining': 60,
    'eta_days': null,
    'created_at': '2026-07-13T10:00:00Z',
    'updated_at': '2026-07-16T10:00:00Z',
  });

  test('listActive entity listesi döner', () async {
    when(() => remote.listActive()).thenAnswer((_) async => [model]);
    final goals = await repo.listActive();
    expect(goals.length, 1);
    expect(goals.first.title, 'Soru hedefi');
  });

  test('create entity döner', () async {
    when(() => remote.create(any())).thenAnswer((_) async => model);
    final entity = await repo.create({
      'title': 'Soru hedefi',
      'goal_type': 'question',
      'target_value': 100,
    });
    expect(entity.targetValue, 100);
  });

  test('getProgress entity döner', () async {
    when(() => remote.getProgress()).thenAnswer(
      (_) async => GoalProgressModel.fromJson({
        'items': [],
        'active_count': 2,
        'completed_count': 1,
        'average_progress': 33.3,
      }),
    );
    final progress = await repo.getProgress();
    expect(progress.activeCount, 2);
    expect(progress.completedCount, 1);
  });
}
