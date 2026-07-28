import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/achievements/data/datasources/achievement_remote_datasource.dart';
import 'package:studyos_mobile/features/achievements/data/repositories/achievement_repository.dart';
import 'package:studyos_mobile/features/achievements/domain/entities/achievement_entity.dart';

class _MockRemote extends Mock implements AchievementRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late AchievementRepository repo;

  setUp(() {
    remote = _MockRemote();
    repo = AchievementRepository(remote);
  });

  test('listProgress remote sonucu döner', () async {
    const item = AchievementEntity(
      id: '11111111-1111-1111-1111-111111111111',
      code: 'pomodoro_first',
      title: 'İlk Pomodoro',
      description: 'x',
      category: 'pomodoro',
      tier: 'easy',
      points: 10,
      iconKey: 'timer',
      unlocked: true,
    );
    when(() => remote.listProgress()).thenAnswer((_) async => [item]);

    final result = await repo.listProgress();
    expect(result.first.code, 'pomodoro_first');
    expect(result.first.reason, isNull);
  });

  test('explain reason taşır', () async {
    when(() => remote.explain(any())).thenAnswer(
      (_) async => const AchievementExplainEntity(
        achievementId: '11111111-1111-1111-1111-111111111111',
        explanation: 'Açıklama',
        provider: 'null',
        reason: 'Saklanan reason',
        code: 'pomodoro_first',
        title: 'İlk Pomodoro',
        usedFallback: true,
      ),
    );

    final result = await repo.explain('11111111-1111-1111-1111-111111111111');
    expect(result.reason, 'Saklanan reason');
  });
}
