import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/widgets/app_empty_state.dart';
import '../../../../core/widgets/app_error_view.dart';
import '../../../../core/widgets/app_loading_skeleton.dart';
import 'package:dio/dio.dart';

/// RC2 M22.4 — Analytics dashboard (mevcut event aggregation).
class AnalyticsDashboard {
  AnalyticsDashboard({
    required this.days,
    required this.dau,
    required this.sessionCount,
    required this.assessmentCompletion,
    required this.quizCompletion,
    required this.pomodoroStarted,
    required this.nextActionCompleted,
    required this.explainUsed,
    required this.knowledgeUsed,
    required this.coachViewed,
    required this.journeyViewed,
    required this.examDistribution,
    required this.topicDistribution,
    required this.screenUsage,
    required this.dropOff,
    required this.eventTotals,
  });

  final int days;
  final int dau;
  final int sessionCount;
  final int assessmentCompletion;
  final int quizCompletion;
  final int pomodoroStarted;
  final int nextActionCompleted;
  final int explainUsed;
  final int knowledgeUsed;
  final int coachViewed;
  final int journeyViewed;
  final List<MapEntry<String, int>> examDistribution;
  final List<MapEntry<String, int>> topicDistribution;
  final List<MapEntry<String, int>> screenUsage;
  final List<MapEntry<String, int>> dropOff;
  final List<MapEntry<String, int>> eventTotals;

  factory AnalyticsDashboard.fromJson(Map<String, dynamic> json) {
    List<MapEntry<String, int>> named(Object? raw, String nameKey) {
      if (raw is! List) return const [];
      return raw
          .whereType<Map>()
          .map((e) {
            final name = (e[nameKey] ?? e['key'] ?? '').toString();
            final count = (e['count'] ?? e['value'] ?? 0) as num;
            return MapEntry(name, count.toInt());
          })
          .where((e) => e.key.isNotEmpty)
          .toList();
    }

    return AnalyticsDashboard(
      days: (json['days'] as num?)?.toInt() ?? 7,
      dau: (json['dau'] as num?)?.toInt() ?? 0,
      sessionCount: (json['session_count'] as num?)?.toInt() ?? 0,
      assessmentCompletion:
          (json['assessment_completion'] as num?)?.toInt() ?? 0,
      quizCompletion: (json['quiz_completion'] as num?)?.toInt() ?? 0,
      pomodoroStarted: (json['pomodoro_started'] as num?)?.toInt() ?? 0,
      nextActionCompleted:
          (json['next_action_completed'] as num?)?.toInt() ?? 0,
      explainUsed: (json['explain_used'] as num?)?.toInt() ?? 0,
      knowledgeUsed: (json['knowledge_used'] as num?)?.toInt() ?? 0,
      coachViewed: (json['coach_viewed'] as num?)?.toInt() ?? 0,
      journeyViewed: (json['journey_viewed'] as num?)?.toInt() ?? 0,
      examDistribution: named(json['exam_distribution'], 'name'),
      topicDistribution: named(json['topic_distribution'], 'name'),
      screenUsage: named(json['screen_usage'], 'name'),
      dropOff: named(json['drop_off'], 'name'),
      eventTotals: named(json['event_totals'], 'key'),
    );
  }
}

final analyticsDashboardProvider =
    FutureProvider.family<AnalyticsDashboard, int>((ref, days) async {
  final dio = ref.watch(dioClientProvider);
  try {
    final response = await dio.get<Map<String, dynamic>>(
      ApiEndpoints.analyticsDashboard,
      queryParameters: {'days': days},
    );
    final data = response.data?['data'];
    if (data is Map<String, dynamic>) {
      return AnalyticsDashboard.fromJson(data);
    }
    if (data is Map) {
      return AnalyticsDashboard.fromJson(
        data.map((k, v) => MapEntry(k.toString(), v)),
      );
    }
    throw const FormatException('Analytics dashboard boş');
  } on DioException catch (e) {
    throw dioExceptionToAppException(e);
  }
});

class AnalyticsDashboardScreen extends ConsumerWidget {
  const AnalyticsDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(analyticsDashboardProvider(7));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics'),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => ref.invalidate(analyticsDashboardProvider(7)),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: async.when(
        loading: () => const AppLoadingSkeleton(rows: 8),
        error: (e, _) => AppErrorView(
          message: e.toString(),
          onRetry: () => ref.invalidate(analyticsDashboardProvider(7)),
        ),
        data: (d) {
          if (d.eventTotals.isEmpty && d.sessionCount == 0) {
            return const AppEmptyState(
              title: 'Henüz veri yok',
              message: 'Uygulama kullanıldıkça analytics dolacak.',
              icon: Icons.insights_outlined,
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                'Son ${d.days} gün',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _metricChip(context, 'DAU', d.dau),
                  _metricChip(context, 'Session', d.sessionCount),
                  _metricChip(context, 'Assessment', d.assessmentCompletion),
                  _metricChip(context, 'Quiz', d.quizCompletion),
                  _metricChip(context, 'Pomodoro', d.pomodoroStarted),
                  _metricChip(context, 'Next Action', d.nextActionCompleted),
                  _metricChip(context, 'Explain', d.explainUsed),
                  _metricChip(context, 'Knowledge', d.knowledgeUsed),
                  _metricChip(context, 'Coach', d.coachViewed),
                  _metricChip(context, 'Journey', d.journeyViewed),
                ],
              ),
              const SizedBox(height: 24),
              _section(context, 'Exam Distribution', d.examDistribution),
              _section(context, 'Topic Distribution', d.topicDistribution),
              _section(context, 'Screen Usage', d.screenUsage),
              _section(context, 'Drop-off', d.dropOff),
              _section(context, 'Event Totals', d.eventTotals),
            ],
          );
        },
      ),
    );
  }

  Widget _metricChip(BuildContext context, String label, int value) {
    return Chip(
      label: Text('$label · $value'),
      visualDensity: VisualDensity.compact,
    );
  }

  Widget _section(
    BuildContext context,
    String title,
    List<MapEntry<String, int>> items,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          if (items.isEmpty)
            Text(
              'Veri yok',
              style: Theme.of(context).textTheme.bodySmall,
            )
          else
            ...items.take(12).map(
                  (e) => ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(e.key),
                    trailing: Text('${e.value}'),
                  ),
                ),
        ],
      ),
    );
  }
}
