import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:studyos_mobile/features/statistics/data/datasources/statistics_remote_datasource.dart';
import 'package:studyos_mobile/features/statistics/data/models/statistics_models.dart';
import 'package:studyos_mobile/features/statistics/data/repositories/statistics_repository_impl.dart';

class _MockRemote extends Mock implements StatisticsRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late StatisticsRepositoryImpl repository;

  setUp(() {
    remote = _MockRemote();
    repository = StatisticsRepositoryImpl(remote);
  });

  test('getOverview maps to entity', () async {
    when(() => remote.getOverview()).thenAnswer(
      (_) async => StatisticsOverviewModel.fromJson({
        'total_study_minutes': 10,
        'today_study_minutes': 5,
        'today_questions': 1,
        'week_study_minutes': 10,
        'month_study_minutes': 10,
        'total_sessions': 1,
        'total_pomodoros': 1,
        'completed_plans': 0,
        'total_questions': 1,
        'average_session_minutes': 5.0,
        'longest_session_minutes': 5,
        'streak_days': 1,
      }),
    );

    final entity = await repository.getOverview();
    expect(entity.totalPomodoros, 1);
    expect(entity.streakDays, 1);
  });

  test('getSubjects maps distribution', () async {
    when(() => remote.getSubjects()).thenAnswer(
      (_) async => StatisticsDistributionModel.fromJson({
        'total_minutes': 20,
        'items': [
          {
            'name': 'Serbest',
            'study_minutes': 20,
            'session_count': 1,
            'question_count': 0,
            'percentage': 100.0,
          },
        ],
      }),
    );

    final entity = await repository.getSubjects();
    expect(entity.items.first.name, 'Serbest');
  });
}
