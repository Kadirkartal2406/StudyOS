import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/features/subjects/domain/entities/subject_hub_entity.dart';
import 'package:studyos_mobile/features/subjects/presentation/providers/subject_hub_provider.dart';
import 'package:studyos_mobile/features/subjects/presentation/screens/subject_hub_screen.dart';

const _hub = SubjectHubEntity(
  subject: SubjectHubIdentity(
    subjectCode: 'tyt_matematik',
    subjectName: 'Matematik',
    section: 'tyt',
  ),
  progress: SubjectHubProgress(
    progressPct: 40,
    accuracy: 70,
    totalQuestions: 100,
    studyMinutes: 200,
  ),
  today: SubjectHubToday(studyMinutes: 25),
  revision: SubjectHubRevision(),
  plans: SubjectHubPlans(),
  examSummary: SubjectHubExamSummary(),
  resources: SubjectHubResources(),
  flashcards: SubjectHubFlashcards(),
  topics: SubjectHubTopics(
    count: 2,
    items: [
      TopicCatalogItem(
        topicCode: 'tyt_mat_problemler',
        topicName: 'Problemler',
        subjectCode: 'tyt_matematik',
      ),
      TopicCatalogItem(
        topicCode: 'tyt_mat_geometri',
        topicName: 'Geometri',
        subjectCode: 'tyt_matematik',
      ),
    ],
  ),
  ai: SubjectHubAi(),
  activeExamType: 'yks',
);

void main() {
  testWidgets('Subject Container: topics merkez; modül launcher yok', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          subjectHubProvider('tyt_matematik').overrideWith(
            (ref) async => _hub,
          ),
        ],
        child: const MaterialApp(
          home: SubjectHubScreen(subjectCode: 'tyt_matematik'),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Konular'), findsOneWidget);
    expect(find.text('Problemler'), findsOneWidget);
    expect(find.text('Geometri'), findsOneWidget);
    expect(find.textContaining('ilerleme'), findsOneWidget);

    expect(find.text('Sorular'), findsNothing);
    expect(find.text('Tekrar'), findsNothing);
    expect(find.text('Pomodoro'), findsNothing);
    expect(find.text('Planner'), findsNothing);
    expect(find.text('Kaynaklar'), findsNothing);
    expect(find.text('AI Coach'), findsNothing);
    expect(find.text('Flashcards'), findsNothing);
    expect(find.text('Denemeler'), findsNothing);
  });

  testWidgets('Topic tap Work Surface route açar', (tester) async {
    final router = GoRouter(
      initialLocation: '/subjects/tyt_matematik',
      routes: [
        GoRoute(
          path: '/subjects/:subjectCode',
          builder: (_, __) => const SubjectHubScreen(subjectCode: 'tyt_matematik'),
          routes: [
            GoRoute(
              path: 'topics/:topicCode',
              builder: (_, state) => Scaffold(
                body: Text('WS:${state.pathParameters['topicCode']}'),
              ),
            ),
          ],
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          subjectHubProvider('tyt_matematik').overrideWith(
            (ref) async => _hub,
          ),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Problemler'));
    await tester.pumpAndSettle();

    expect(find.text('WS:tyt_mat_problemler'), findsOneWidget);
  });
}
