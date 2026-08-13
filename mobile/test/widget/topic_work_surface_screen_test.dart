import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/onboarding/domain/entities/learning_profile_entity.dart';
import 'package:studyos_mobile/features/onboarding/presentation/providers/learning_profile_provider.dart';
import 'package:studyos_mobile/features/subjects/domain/entities/topic_notebook_entity.dart';
import 'package:studyos_mobile/features/subjects/domain/entities/topic_work_surface_entity.dart';
import 'package:studyos_mobile/features/subjects/presentation/providers/topic_notebook_provider.dart';
import 'package:studyos_mobile/features/subjects/presentation/providers/topic_work_surface_provider.dart';
import 'package:studyos_mobile/features/subjects/presentation/screens/topic_work_surface_screen.dart';
import 'package:studyos_mobile/features/topic_quiz/data/topic_test_remote_datasource.dart';
import 'package:studyos_mobile/features/topic_quiz/presentation/providers/topic_test_catalog_provider.dart';

const _surface = TopicWorkSurfaceEntity(
  learningState: TopicLearningStateEntity(
    subjectCode: 'tyt_matematik',
    topicCode: 'tyt_mat_problemler',
    topicName: 'Problemler',
    subjectName: 'TYT Matematik',
    summaryLine: 'Bu konu üzerinde çalışmaya hazırsın.',
  ),
  primaryAction: TopicPrimaryActionEntity(
    title: 'Bu konu üzerinde çalış',
    subtitle: 'Problemler · 25 dk',
    reason: 'Bu konu üzerinde çalışmaya devam et.',
    actionType: 'study_plan',
    deepLinkHint: '/subjects/tyt_matematik/topics/tyt_mat_problemler',
    purpose: 'study',
    toolHint: 'pomodoro',
    subjectCode: 'tyt_matematik',
    topicCode: 'tyt_mat_problemler',
  ),
  secondaryTools: [
    TopicSecondaryToolEntity(
      id: 'pomodoro',
      label: 'Pomodoro',
      deepLinkHint: '/pomodoro?subject_code=tyt_matematik',
    ),
    TopicSecondaryToolEntity(
      id: 'resources',
      label: 'Kaynak',
      deepLinkHint: '/resources?subject_code=tyt_matematik',
    ),
    TopicSecondaryToolEntity(
      id: 'questions',
      label: 'Soru Kaydı',
      deepLinkHint: '/questions?subject_code=tyt_matematik',
    ),
    TopicSecondaryToolEntity(
      id: 'revision',
      label: 'Revision Durumu',
      deepLinkHint: '/revisions?subject_code=tyt_matematik',
    ),
  ],
);

const _emptyCatalog = TopicTestCatalog(
  exam: 'tyt',
  subjectCode: 'tyt_matematik',
  topicCode: 'tyt_mat_problemler',
  tests: [],
);

const _profile = LearningProfileEntity(
  userId: 'u1',
  journeyStage: 'active',
  onboardingCompleted: true,
  onboardingSkipped: false,
  onboardingRequired: false,
  dailyStudyMinutes: 120,
  availableDays: [1, 2, 3, 4, 5],
  availableHours: 3,
  baselineLevel: 'medium',
  activeExamType: 'tyt',
  primaryExamType: 'tyt',
);

const _notebook = TopicNotebookEntity(
  topicCode: 'tyt_mat_problemler',
  subjectCode: 'tyt_matematik',
  topicName: 'Problemler',
  confidenceLevel: 'unknown',
  beliefPct: 0,
  trend: 'stable',
  needsExplain: false,
  sampleCount: 0,
  effortMinutes: 0,
  resourceCount: 0,
  resources: [],
  displayTitle: 'Notebook',
  knowledgeReady: false,
  knowledgeChunkCount: 0,
  knowledgeCitationCount: 0,
  explainAvailable: false,
  quizAvailable: false,
  quizDifficulty: 'easy',
);

List<Override> _overrides({required TopicTestCatalog catalog}) {
  const key = (subjectCode: 'tyt_matematik', topicCode: 'tyt_mat_problemler');
  return [
    topicWorkSurfaceProvider(key).overrideWith((ref) async => _surface),
    learningProfileProvider.overrideWith((ref) async => _profile),
    topicTestCatalogForTopicProvider(key).overrideWith((ref) async => catalog),
    topicNotebookProvider(key).overrideWith((ref) async => _notebook),
  ];
}

void main() {
  testWidgets('Work Surface: Konu Testleri var, Soru üret yok', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: _overrides(catalog: _emptyCatalog),
        child: const MaterialApp(
          home: TopicWorkSurfaceScreen(
            subjectCode: 'tyt_matematik',
            topicCode: 'tyt_mat_problemler',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(
      find.text('Konu Testleri'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.pumpAndSettle();

    expect(find.text('Konu Testleri'), findsWidgets);
    expect(find.text('Bu konu için yeni testler hazırlanıyor.'), findsOneWidget);
    expect(find.text('Soru üret'), findsNothing);
    expect(find.text('Soruları Üret'), findsNothing);
    expect(find.text('Quiz'), findsNothing);
  });

  testWidgets('Work Surface: published testler listelenir', (tester) async {
    final catalog = TopicTestCatalog(
      exam: 'tyt',
      subjectCode: 'tyt_matematik',
      topicCode: 'tyt_mat_problemler',
      tests: [
        TopicTestListItem(
          id: 't1',
          weekId: '2026-W33',
          difficulty: 'easy',
          ordinal: 1,
          questionCount: 10,
          title: 'Kolay Test 1',
          userStatus: 'not_started',
        ),
        TopicTestListItem(
          id: 't2',
          weekId: '2026-W33',
          difficulty: 'medium',
          ordinal: 1,
          questionCount: 10,
          title: 'Orta Test 1',
          userStatus: 'submitted',
          accuracyPct: 80,
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: _overrides(catalog: catalog),
        child: const MaterialApp(
          home: TopicWorkSurfaceScreen(
            subjectCode: 'tyt_matematik',
            topicCode: 'tyt_mat_problemler',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(
      find.text('Kolay Test 1'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.pumpAndSettle();

    expect(find.text('Kolay Test 1'), findsOneWidget);
    expect(find.textContaining('10 soru'), findsWidgets);
    expect(find.text('Soru üret'), findsNothing);
  });
}
