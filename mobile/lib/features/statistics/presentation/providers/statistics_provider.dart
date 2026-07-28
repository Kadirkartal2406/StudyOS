import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/statistics_remote_datasource.dart';
import '../../data/repositories/statistics_repository_impl.dart';
import '../../domain/repositories/statistics_repository.dart';
import '../../domain/usecases/statistics_usecases.dart';
import 'statistics_state.dart';

final _remoteProvider = Provider<StatisticsRemoteDatasource>((ref) {
  return StatisticsRemoteDatasource(ref.watch(dioClientProvider));
});

final statisticsRepositoryProvider = Provider<StatisticsRepository>((ref) {
  return StatisticsRepositoryImpl(ref.watch(_remoteProvider));
});

class StatisticsNotifier extends StateNotifier<StatisticsState> {
  StatisticsNotifier({
    required GetStatisticsOverviewUsecase getOverview,
    required GetStatisticsDailyUsecase getDaily,
    required GetStatisticsWeeklyUsecase getWeekly,
    required GetStatisticsMonthlyUsecase getMonthly,
    required GetStatisticsSubjectsUsecase getSubjects,
    required StatisticsRepository repository,
  })  : _getOverview = getOverview,
        _getDaily = getDaily,
        _getWeekly = getWeekly,
        _getMonthly = getMonthly,
        _getSubjects = getSubjects,
        _repository = repository,
        super(const StatisticsInitial()) {
    load();
  }

  final GetStatisticsOverviewUsecase _getOverview;
  final GetStatisticsDailyUsecase _getDaily;
  final GetStatisticsWeeklyUsecase _getWeekly;
  final GetStatisticsMonthlyUsecase _getMonthly;
  final GetStatisticsSubjectsUsecase _getSubjects;
  final StatisticsRepository _repository;

  Future<void> load() async {
    state = const StatisticsLoading();
    try {
      final overview = await _getOverview();
      final daily = await _getDaily();
      final weekly = await _getWeekly();
      final monthly = await _getMonthly();
      final subjects = await _getSubjects();
      final heatmap = await _repository.getHeatmap();
      state = StatisticsLoaded(
        overview: overview,
        daily: daily,
        weekly: weekly,
        monthly: monthly,
        subjects: subjects,
        heatmap: heatmap,
      );
    } on AppException catch (e) {
      state = StatisticsError(e.message);
    } catch (_) {
      state = const StatisticsError('İstatistikler yüklenemedi');
    }
  }
}

final statisticsProvider =
    StateNotifierProvider<StatisticsNotifier, StatisticsState>((ref) {
  final repo = ref.watch(statisticsRepositoryProvider);
  return StatisticsNotifier(
    getOverview: GetStatisticsOverviewUsecase(repo),
    getDaily: GetStatisticsDailyUsecase(repo),
    getWeekly: GetStatisticsWeeklyUsecase(repo),
    getMonthly: GetStatisticsMonthlyUsecase(repo),
    getSubjects: GetStatisticsSubjectsUsecase(repo),
    repository: repo,
  );
});
