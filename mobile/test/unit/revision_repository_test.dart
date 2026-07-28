import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/revision/data/datasources/revision_remote_datasource.dart';
import 'package:studyos_mobile/features/revision/data/repositories/revision_repository.dart';
import 'package:studyos_mobile/features/revision/domain/entities/revision_entity.dart';

class _MockRemote extends Mock implements RevisionRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late RevisionRepository repo;

  setUpAll(() {
    registerFallbackValue(<String, dynamic>{});
  });

  setUp(() {
    remote = _MockRemote();
    repo = RevisionRepository(remote);
  });

  test('create maps body and returns item with reason', () async {
    const item = RevisionItemEntity(
      id: '11111111-1111-1111-1111-111111111111',
      title: 'Matematik tekrarı',
      subject: 'Matematik',
      sourceType: 'manual',
      difficulty: 3,
      reason: 'Zayıf konu',
      status: 'active',
    );
    when(() => remote.create(any())).thenAnswer((_) async => item);

    final result = await repo.create(
      title: 'Matematik tekrarı',
      subject: 'Matematik',
      reason: 'Zayıf konu',
    );

    expect(result.reason, 'Zayıf konu');
    expect(result.difficulty, 3);
    verify(
      () => remote.create({
        'title': 'Matematik tekrarı',
        'subject': 'Matematik',
        'reason': 'Zayıf konu',
        'difficulty': 3,
        'source_type': 'manual',
      }),
    ).called(1);
  });

  test('review grade iletir', () async {
    const item = RevisionItemEntity(
      id: '11111111-1111-1111-1111-111111111111',
      title: 'x',
      subject: 'Fizik',
      sourceType: 'manual',
      difficulty: 2,
      reason: 'r',
      status: 'active',
    );
    when(() => remote.review(any(), any())).thenAnswer((_) async => item);

    await repo.review(item.id, 'good');
    verify(() => remote.review(item.id, 'good')).called(1);
  });
}
