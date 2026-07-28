import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/dashboard/data/datasources/dashboard_remote_datasource.dart';
import 'package:studyos_mobile/features/dashboard/data/models/dashboard_model.dart';
import 'package:studyos_mobile/features/dashboard/data/repositories/dashboard_repository_impl.dart';

class _MockDashboardRemoteDatasource extends Mock
    implements DashboardRemoteDatasource {}

void main() {
  late _MockDashboardRemoteDatasource datasource;
  late DashboardRepositoryImpl repository;

  setUp(() {
    datasource = _MockDashboardRemoteDatasource();
    repository = DashboardRepositoryImpl(datasource);
  });

  test('getDashboard datasource\'tan gelen modeli entity\'e dönüştürür', () async {
    const model = DashboardModel(
      firstName: 'Kadir',
      dailyStudyGoalMinutes: 120,
      todayStudyMinutes: 0,
      todayQuestionsSolved: 0,
      todayStudiedTopic: null,
      dailyProgressPercentage: 0.0,
      lastLoginAt: null,
    );
    when(() => datasource.getDashboard()).thenAnswer((_) async => model);

    final entity = await repository.getDashboard();

    expect(entity.firstName, 'Kadir');
    expect(entity.dailyStudyGoalMinutes, 120);
    verify(() => datasource.getDashboard()).called(1);
  });

  test('datasource hata fırlattığında repository de fırlatır', () async {
    when(() => datasource.getDashboard()).thenThrow(Exception('ağ hatası'));

    expect(() => repository.getDashboard(), throwsException);
  });
}
