import '../../domain/entities/revision_entity.dart';
import '../datasources/revision_remote_datasource.dart';

class RevisionRepository {
  RevisionRepository(this._remote);

  final RevisionRemoteDatasource _remote;

  Future<List<RevisionItemEntity>> listToday() => _remote.listToday();

  Future<List<RevisionItemEntity>> listOverdue() => _remote.listOverdue();

  Future<List<RevisionItemEntity>> listAll() => _remote.listAll();

  Future<RevisionItemEntity> create({
    required String title,
    required String subject,
    String? topic,
    String? reason,
    int difficulty = 3,
  }) {
    return _remote.create({
      'title': title,
      'subject': subject,
      if (topic != null) 'topic': topic,
      if (reason != null) 'reason': reason,
      'difficulty': difficulty,
      'source_type': 'manual',
    });
  }

  Future<RevisionItemEntity> review(String id, String grade) =>
      _remote.review(id, grade);

  Future<RevisionItemEntity> skip(String id) => _remote.skip(id);

  Future<RevisionItemEntity> postpone(String id, {int days = 3}) =>
      _remote.postpone(id, days: days);

  Future<RevisionExplainEntity> explain(String id) => _remote.explain(id);

  Future<RevisionGenerateResult> generate() => _remote.generate();

  Future<RevisionStatisticsEntity> statistics() => _remote.statistics();
}
