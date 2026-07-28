import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/question_tracking/data/datasources/question_tracking_remote_datasource.dart';
import 'package:studyos_mobile/features/question_tracking/data/models/question_record_model.dart';
import 'package:studyos_mobile/features/question_tracking/data/repositories/question_tracking_repository_impl.dart';

class _MockRemote extends Mock implements QuestionTrackingRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late QuestionTrackingRepositoryImpl repo;

  setUp(() {
    remote = _MockRemote();
    repo = QuestionTrackingRepositoryImpl(remote);
  });

  final model = QuestionRecordModel.fromJson({
    'id': '11111111-1111-1111-1111-111111111111',
    'user_id': '22222222-2222-2222-2222-222222222222',
    'subject': 'Fizik',
    'topic': null,
    'question_count': 10,
    'correct_count': 7,
    'wrong_count': 2,
    'blank_count': 1,
    'duration_minutes': 20,
    'difficulty': null,
    'source': null,
    'exam_type': null,
    'note': null,
    'net_score': 6.5,
    'created_at': '2026-07-16T10:00:00Z',
    'updated_at': '2026-07-16T10:00:00Z',
  });

  test('list pagination entity döner', () async {
    when(
      () => remote.list(
        page: any(named: 'page'),
        pageSize: any(named: 'pageSize'),
        subject: any(named: 'subject'),
        topic: any(named: 'topic'),
        examType: any(named: 'examType'),
        source: any(named: 'source'),
      ),
    ).thenAnswer(
      (_) async => (
        [model],
        {'page': 1, 'page_size': 20, 'total_items': 1, 'total_pages': 1},
      ),
    );

    final page = await repo.list();
    expect(page.totalItems, 1);
    expect(page.items.first.subject, 'Fizik');
  });

  test('create entity döner', () async {
    when(() => remote.create(any())).thenAnswer((_) async => model);
    final entity = await repo.create({'subject': 'Fizik', 'question_count': 10});
    expect(entity.questionCount, 10);
  });
}
