import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:studyos_mobile/features/question_tracking/domain/entities/question_record_entity.dart';
import 'package:studyos_mobile/features/question_tracking/domain/repositories/question_tracking_repository.dart';
import 'package:studyos_mobile/features/question_tracking/presentation/providers/question_tracking_provider.dart';
import 'package:studyos_mobile/features/question_tracking/presentation/screens/question_list_screen.dart';

class _MockRepo extends Mock implements QuestionTrackingRepository {}

void main() {
  late _MockRepo repo;

  setUp(() {
    repo = _MockRepo();
  });

  testWidgets('liste boşken boş durum gösterir', (tester) async {
    when(
      () => repo.list(
        page: any(named: 'page'),
        pageSize: any(named: 'pageSize'),
        subject: any(named: 'subject'),
        topic: any(named: 'topic'),
        examType: any(named: 'examType'),
        source: any(named: 'source'),
      ),
    ).thenAnswer(
      (_) async => const QuestionListPage(
        items: [],
        page: 1,
        pageSize: 20,
        totalItems: 0,
        totalPages: 0,
      ),
    );

    final router = GoRouter(
      initialLocation: '/questions',
      routes: [
        GoRoute(
          path: '/questions',
          builder: (_, __) => const QuestionListScreen(),
        ),
        GoRoute(
          path: '/questions/add',
          builder: (_, __) => const Scaffold(body: Text('add')),
        ),
        GoRoute(
          path: '/questions/statistics',
          builder: (_, __) => const Scaffold(body: Text('stats')),
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          questionTrackingRepositoryProvider.overrideWithValue(repo),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('Soru Takibi'), findsOneWidget);
    expect(find.text('Henüz soru kaydı yok'), findsOneWidget);
  });
}
