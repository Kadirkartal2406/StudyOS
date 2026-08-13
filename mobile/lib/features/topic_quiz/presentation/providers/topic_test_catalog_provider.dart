import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../data/topic_test_remote_datasource.dart';

typedef TopicTestCatalogKey = ({
  String exam,
  String subjectCode,
  String topicCode,
});

/// Published topic tests for a topic (Gemini-free).
final topicTestCatalogProvider =
    FutureProvider.family<TopicTestCatalog, TopicTestCatalogKey>((ref, key) async {
  return ref.watch(topicTestDatasourceProvider).listCatalog(
        exam: key.exam,
        subjectCode: key.subjectCode,
        topicCode: key.topicCode,
      );
});

/// Resolves exam for catalog using learning profile active exam.
final topicTestCatalogForTopicProvider = FutureProvider.family<
    TopicTestCatalog,
    ({String subjectCode, String topicCode})>((ref, key) async {
  final profile = await ref.watch(learningProfileProvider.future);
  final exam = (profile.activeExamType ??
          profile.primaryExamType ??
          'kpss')
      .trim()
      .toLowerCase();
  return ref.watch(
    topicTestCatalogProvider((
      exam: exam,
      subjectCode: key.subjectCode,
      topicCode: key.topicCode,
    )).future,
  );
});
