import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';

class ConfidenceTrendEntity {
  const ConfidenceTrendEntity({
    required this.subjectCode,
    required this.topicCode,
    required this.topicName,
    required this.confidenceLevel,
    required this.trend,
    required this.trendLabel,
    this.beliefPct,
  });

  final String subjectCode;
  final String topicCode;
  final String topicName;
  final String confidenceLevel;
  final String trend;
  final String trendLabel;
  final double? beliefPct;
}

class JourneyTrendsEntity {
  const JourneyTrendsEntity({
    this.rising = const [],
    this.falling = const [],
    this.stable = const [],
  });

  final List<ConfidenceTrendEntity> rising;
  final List<ConfidenceTrendEntity> falling;
  final List<ConfidenceTrendEntity> stable;
}

final journeyTrendsProvider =
    FutureProvider.autoDispose<JourneyTrendsEntity>((ref) async {
  final dio = ref.watch(dioClientProvider);
  final response = await dio.get<Map<String, dynamic>>(ApiEndpoints.journeyTrends);
  final data = response.data?['data'] as Map<String, dynamic>? ?? {};

  List<ConfidenceTrendEntity> parse(String key) {
    return (data[key] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => ConfidenceTrendEntity(
            subjectCode: m['subject_code'] as String? ?? '',
            topicCode: m['topic_code'] as String? ?? '',
            topicName: m['topic_name'] as String? ?? '',
            confidenceLevel: m['confidence_level'] as String? ?? 'unknown',
            trend: m['trend'] as String? ?? 'stable',
            trendLabel: m['trend_label'] as String? ?? '',
            beliefPct: (m['belief_pct'] as num?)?.toDouble(),
          ),
        )
        .toList();
  }

  return JourneyTrendsEntity(
    rising: parse('rising'),
    falling: parse('falling'),
    stable: parse('stable'),
  );
});
