import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/ai_coach/domain/entities/ai_coach_entities.dart';
import 'package:studyos_mobile/features/ai_coach/domain/repositories/ai_coach_repository.dart';
import 'package:studyos_mobile/features/ai_coach/presentation/providers/ai_coach_provider.dart';
import 'package:studyos_mobile/features/ai_coach/presentation/screens/ai_coach_screen.dart';

class _FakeRepo implements AiCoachRepository {
  @override
  Future<AiOverviewEntity> getOverview() async {
    return const AiOverviewEntity(
      hasEnoughData: true,
      streakDays: 3,
      averageDailyMinutes: 40,
      correctRate: 70,
      topRecommendation: AiRecommendationEntity(
        code: 'keep_going',
        message: 'Ritmini koru',
        priority: 10,
        category: 'motivation',
      ),
    );
  }

  @override
  Future<List<AiRecommendationEntity>> getRecommendations() async {
    return const [
      AiRecommendationEntity(
        code: 'keep_going',
        message: 'Ritmini koru',
        priority: 10,
        category: 'motivation',
      ),
    ];
  }

  @override
  Future<AiTrendsEntity> getTrends() async {
    return const AiTrendsEntity(
      weeklyStudyMinutes: 120,
      previousWeekStudyMinutes: 100,
      studyMinutesDeltaPct: 20,
      weeklyQuestions: 30,
      dailySeries: [
        AiTrendPointEntity(label: 'Pzt', studyMinutes: 40, questionCount: 10),
      ],
    );
  }

  @override
  Future<AiPerformanceEntity> getPerformance() async {
    return const AiPerformanceEntity(
      correctRate: 70,
      totalQuestions: 50,
      totalNet: 35,
    );
  }

  @override
  Future<AiProductivityEntity> getProductivity() async {
    return const AiProductivityEntity(
      mostProductiveHour: 20,
      mostProductiveWeekdayLabel: 'Çarşamba',
      streakDays: 3,
      idleDaysLast14: 2,
    );
  }
}

void main() {
  testWidgets('AI Coach ekranı bölüm başlıklarını gösterir', (tester) async {
    tester.view.physicalSize = const Size(800, 2400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          aiCoachRepositoryProvider.overrideWithValue(_FakeRepo()),
        ],
        child: const MaterialApp(home: AiCoachScreen()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('AI Çalışma Koçu'), findsOneWidget);
    expect(find.text('Özet İçgörüler'), findsOneWidget);
    expect(find.text('Öneriler'), findsOneWidget);
    expect(find.text('Trendler'), findsOneWidget);
    expect(find.text('Performans'), findsOneWidget);
    expect(find.text('Verimlilik'), findsOneWidget);
    expect(find.textContaining('Ritmini koru'), findsWidgets);
  });
}
