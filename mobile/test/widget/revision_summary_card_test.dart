import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/features/dashboard/presentation/widgets/revision_summary_card.dart';

void main() {
  testWidgets('RevisionSummaryCard boş durum', (tester) async {
    final router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/',
          builder: (_, __) => const Scaffold(body: RevisionSummaryCard()),
        ),
        GoRoute(
          path: '/revisions',
          builder: (_, __) => const Scaffold(body: Text('revisions')),
        ),
      ],
    );

    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    expect(find.text('Bugün tekrar yok'), findsOneWidget);
  });

  testWidgets('RevisionSummaryCard reason gösterir', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: RevisionSummaryCard(
            dueToday: 2,
            overdue: 1,
            dueThisWeek: 4,
            nextTitle: 'Matematik tekrarı',
            overviewReason: 'Doğruluk düşük',
          ),
        ),
      ),
    );

    expect(find.text('Bugünkü Tekrarlar'), findsOneWidget);
    expect(find.textContaining('Doğruluk düşük'), findsOneWidget);
  });
}
