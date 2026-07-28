import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/ai_coach/data/datasources/ai_coach_remote_datasource.dart';
import 'package:studyos_mobile/features/ai_coach/data/models/ai_coach_models.dart';
import 'package:studyos_mobile/features/ai_coach/data/repositories/ai_coach_repository_impl.dart';

class _MockRemote extends Mock implements AiCoachRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late AiCoachRepositoryImpl repository;

  setUp(() {
    remote = _MockRemote();
    repository = AiCoachRepositoryImpl(remote);
  });

  test('getOverview maps to entity', () async {
    when(() => remote.getOverview()).thenAnswer(
      (_) async => AiOverviewModel.fromJson({
        'has_enough_data': false,
        'streak_days': 0,
        'top_recommendation': {
          'code': 'insufficient_data',
          'message': 'Daha fazla veri gerekli',
          'priority': 1,
          'category': 'onboarding',
        },
      }),
    );

    final entity = await repository.getOverview();
    expect(entity.hasEnoughData, isFalse);
    expect(entity.topRecommendation?.code, 'insufficient_data');
  });

  test('getRecommendations maps list', () async {
    when(() => remote.getRecommendations()).thenAnswer(
      (_) async => [
        AiRecommendationModel.fromJson({
          'code': 'idle_streak',
          'message': '3 gündür boşsun',
          'priority': 5,
          'category': 'habit',
        }),
      ],
    );

    final items = await repository.getRecommendations();
    expect(items, hasLength(1));
    expect(items.first.code, 'idle_streak');
  });

  test('getProductivity maps hours', () async {
    when(() => remote.getProductivity()).thenAnswer(
      (_) async => AiProductivityModel.fromJson({
        'most_productive_hour': 21,
        'least_productive_hour': 6,
        'most_productive_weekday_label': 'Salı',
        'hour_minutes': List<int>.filled(24, 0),
        'weekday_minutes': List<int>.filled(7, 0),
        'streak_days': 2,
        'idle_days_last_14': 5,
      }),
    );

    final entity = await repository.getProductivity();
    expect(entity.mostProductiveHour, 21);
    expect(entity.mostProductiveWeekdayLabel, 'Salı');
  });
}
