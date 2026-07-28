import '../../domain/entities/learning_profile_entity.dart';
import '../datasources/learning_profile_remote_datasource.dart';

class LearningProfileRepository {
  LearningProfileRepository(this._remote);

  final LearningProfileRemoteDatasource _remote;

  Future<OnboardingStatusEntity> status() => _remote.status();

  Future<LearningProfileEntity> getProfile() => _remote.getProfile();

  Future<LearningProfileEntity> complete(Map<String, dynamic> body) =>
      _remote.complete(body);

  Future<String> welcomeTone({
    required String step,
    required String firstName,
    String? examHint,
    String? lastAnswer,
  }) =>
      _remote.welcomeTone(
        step: step,
        firstName: firstName,
        examHint: examHint,
        lastAnswer: lastAnswer,
      );

  Future<LearningProfileEntity> skip() => _remote.skip();

  Future<LearningProfileEntity> setActiveExam(String examType) =>
      _remote.setActiveExam(examType);

  Future<void> addExamTarget(Map<String, dynamic> body) =>
      _remote.addExamTarget(body);

  Future<List<UserSubjectEntity>> mySubjects() => _remote.mySubjects();
}
