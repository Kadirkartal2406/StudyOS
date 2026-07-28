import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:studyos_mobile/features/dashboard/presentation/widgets/journey_progress_card.dart';

void main() {
  testWidgets('JourneyProgressCard progress ve CTA gösterir', (tester) async {
    final router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/',
          builder: (_, __) => const Scaffold(
            body: JourneyProgressCard(
              todayPct: 40,
              weekPct: 25,
              monthPct: 10,
              overallPct: 30,
              journeyStage: 'learning',
              onboardingRequired: true,
              primaryExamType: 'yks',
            ),
          ),
        ),
        GoRoute(
          path: '/onboarding',
          builder: (_, __) => const Scaffold(body: Text('onboarding')),
        ),
      ],
    );
    await tester.pumpWidget(MaterialApp.router(routerConfig: router));
    expect(find.text('Yolculuk'), findsOneWidget);
    expect(find.text('Bugün'), findsOneWidget);
    expect(find.text('Kurulum'), findsOneWidget);
    expect(find.textContaining('YKS'), findsOneWidget);
  });
}
