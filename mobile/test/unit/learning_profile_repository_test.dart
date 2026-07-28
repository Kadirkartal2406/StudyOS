import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/onboarding/data/datasources/learning_profile_remote_datasource.dart';
import 'package:studyos_mobile/features/onboarding/data/repositories/learning_profile_repository.dart';
import 'package:studyos_mobile/features/onboarding/domain/entities/learning_profile_entity.dart';

class _MockRemote extends Mock implements LearningProfileRemoteDatasource {}

void main() {
  late _MockRemote remote;
  late LearningProfileRepository repo;

  setUp(() {
    remote = _MockRemote();
    repo = LearningProfileRepository(remote);
  });

  test('status remote sonucu döner', () async {
    when(() => remote.status()).thenAnswer(
      (_) async => const OnboardingStatusEntity(
        onboardingRequired: true,
        onboardingCompleted: false,
        onboardingSkipped: false,
        journeyStage: 'new_user',
        canSkip: false,
      ),
    );
    final result = await repo.status();
    expect(result.onboardingRequired, isTrue);
    expect(result.canSkip, isFalse);
  });

  test('setActiveExam remote çağırır', () async {
    when(() => remote.setActiveExam('yds')).thenAnswer(
      (_) async => const LearningProfileEntity(
        userId: 'u1',
        journeyStage: 'learning',
        onboardingCompleted: true,
        onboardingSkipped: false,
        onboardingRequired: false,
        dailyStudyMinutes: 120,
        availableDays: [0, 1, 2],
        availableHours: 2,
        baselineLevel: 'unknown',
        primaryExamType: 'yks',
        activeExamType: 'yds',
      ),
    );
    final result = await repo.setActiveExam('yds');
    expect(result.activeExamType, 'yds');
    expect(result.primaryExamType, 'yks');
  });
}
