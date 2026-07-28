import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';

class CoachWeeklyEntity {
  const CoachWeeklyEntity({
    required this.body,
    required this.weeklySuggestion,
    this.questionsSolved = 0,
    this.studyMinutes = 0,
    this.confidenceDeltaLabel,
    this.strongestTopic,
    this.weakestTopic,
  });

  final String body;
  final String weeklySuggestion;
  final int questionsSolved;
  final int studyMinutes;
  final String? confidenceDeltaLabel;
  final String? strongestTopic;
  final String? weakestTopic;
}

class CoachTimelineItemEntity {
  const CoachTimelineItemEntity({
    required this.period,
    required this.title,
    required this.body,
    this.tone = 'neutral',
  });

  final String period;
  final String title;
  final String body;
  final String tone;
}

class CoachTimelineEntity {
  const CoachTimelineEntity({
    required this.items,
    this.nextGoal,
  });

  final List<CoachTimelineItemEntity> items;
  final String? nextGoal;
}

final coachWeeklyProvider = FutureProvider.autoDispose<CoachWeeklyEntity>((ref) async {
  final dio = ref.watch(dioClientProvider);
  final res = await dio.get<Map<String, dynamic>>(ApiEndpoints.coachWeekly);
  final data = res.data?['data'] as Map<String, dynamic>?;
  final r = data?['reflection'] as Map<String, dynamic>? ?? {};
  return CoachWeeklyEntity(
    body: r['body'] as String? ?? '',
    weeklySuggestion: r['weekly_suggestion'] as String? ?? '',
    questionsSolved: r['questions_solved'] as int? ?? 0,
    studyMinutes: r['study_minutes'] as int? ?? 0,
    confidenceDeltaLabel: r['confidence_delta_label'] as String?,
    strongestTopic: r['strongest_topic'] as String?,
    weakestTopic: r['weakest_topic'] as String?,
  );
});

final coachTimelineProvider =
    FutureProvider.autoDispose<CoachTimelineEntity>((ref) async {
  final dio = ref.watch(dioClientProvider);
  final res = await dio.get<Map<String, dynamic>>(ApiEndpoints.coachTimeline);
  final data = res.data?['data'] as Map<String, dynamic>?;
  final tl = data?['timeline'] as Map<String, dynamic>? ?? {};
  final items = (tl['items'] as List<dynamic>? ?? [])
      .whereType<Map<String, dynamic>>()
      .map(
        (m) => CoachTimelineItemEntity(
          period: m['period'] as String? ?? '',
          title: m['title'] as String? ?? '',
          body: m['body'] as String? ?? '',
          tone: m['tone'] as String? ?? 'neutral',
        ),
      )
      .toList();
  return CoachTimelineEntity(
    items: items,
    nextGoal: tl['next_goal'] as String?,
  );
});
