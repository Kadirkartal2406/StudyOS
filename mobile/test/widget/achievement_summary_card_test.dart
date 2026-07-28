import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/features/dashboard/presentation/widgets/achievement_summary_card.dart';

void main() {
  testWidgets('AchievementSummaryCard boş durum', (tester) async {
    final router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/',
          builder: (_, __) => const Scaffold(body: AchievementSummaryCard()),
        ),
        GoRoute(
          path: '/achievements',
          builder: (_, __) => const Scaffold(body: Text('achievements')),
        ),
      ],
    );
    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    expect(find.text('Henüz rozet yok'), findsOneWidget);
  });

  testWidgets('AchievementSummaryCard reason gösterir', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AchievementSummaryCard(
            totalUnlocked: 2,
            totalPoints: 30,
            recentTitle: 'İlk Pomodoro',
            recentReason: 'total_pomodoros=1',
          ),
        ),
      ),
    );
    expect(find.text('Rozetler'), findsOneWidget);
    expect(find.textContaining('total_pomodoros'), findsOneWidget);
  });
}
