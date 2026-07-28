import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/subjects/domain/entities/topic_work_surface_entity.dart';
import 'package:studyos_mobile/features/subjects/presentation/providers/topic_work_surface_provider.dart';
import 'package:studyos_mobile/features/subjects/presentation/screens/topic_work_surface_screen.dart';

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

void main() {
  testWidgets('Work Surface: Learning State + amaç Primary + 4 secondary', (
    tester,
  ) async {
    const key = (subjectCode: 'tyt_matematik', topicCode: 'tyt_mat_problemler');

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          topicWorkSurfaceProvider(key).overrideWith((ref) async => _surface),
        ],
        child: const MaterialApp(
          home: TopicWorkSurfaceScreen(
            subjectCode: 'tyt_matematik',
            topicCode: 'tyt_mat_problemler',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Learning State'), findsOneWidget);
    expect(find.text('Problemler'), findsWidgets);
    expect(find.text('Bu konu üzerinde çalış'), findsOneWidget);
    expect(find.text('Pomodoro'), findsOneWidget);
    expect(find.text('Kaynak'), findsOneWidget);
    expect(find.text('Soru Kaydı'), findsOneWidget);
    expect(find.text('Revision Durumu'), findsOneWidget);
    expect(find.text('AI Explain'), findsNothing);
    expect(find.text('NotebookLM'), findsNothing);
  });
}
