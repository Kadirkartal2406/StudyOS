import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/ai_coach_provider.dart';
import '../providers/ai_coach_state.dart';
import '../widgets/ai_coach_cards.dart';

/// Sprint-2.0 — AI Study Coach (rule-based insight UI; no LLM chat).
class AiCoachScreen extends ConsumerWidget {
  const AiCoachScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(aiCoachProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Çalışma Koçu'),
      ),
      body: SafeArea(
        child: switch (state) {
          AiCoachInitial() || AiCoachLoading() => const Center(
              child: CircularProgressIndicator(),
            ),
          AiCoachError(:final message) => Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(message, textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: () =>
                          ref.read(aiCoachProvider.notifier).load(),
                      child: const Text('Tekrar Dene'),
                    ),
                  ],
                ),
              ),
            ),
          AiCoachLoaded() => RefreshIndicator(
              onRefresh: () => ref.read(aiCoachProvider.notifier).load(),
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  _InsightsCard(state: state),
                  const SizedBox(height: 16),
                  _RecommendationsCard(state: state),
                  const SizedBox(height: 16),
                  _TrendsCard(state: state),
                  const SizedBox(height: 16),
                  _PerformanceCard(state: state),
                  const SizedBox(height: 16),
                  _ProductivityCard(state: state),
                  const SizedBox(height: 20),
                ],
              ),
            ),
        },
      ),
    );
  }
}

class _InsightsCard extends StatelessWidget {
  const _InsightsCard({required this.state});

  final AiCoachLoaded state;

  @override
  Widget build(BuildContext context) {
    final o = state.overview;
    return AiSectionCard(
      title: 'Özet İçgörüler',
      icon: Icons.auto_awesome_rounded,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!o.hasEnoughData)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(
                'Henüz yeterli veri yok. Birkaç çalışma ve soru kaydı ekledikçe '
                'öneriler güçlenecek.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              SizedBox(
                width: 150,
                child: AiMetricTile(
                  label: 'Streak',
                  value: '${o.streakDays} gün',
                ),
              ),
              SizedBox(
                width: 150,
                child: AiMetricTile(
                  label: 'Ort. günlük süre',
                  value: '${o.averageDailyMinutes.toStringAsFixed(0)} dk',
                ),
              ),
              SizedBox(
                width: 150,
                child: AiMetricTile(
                  label: 'Doğruluk',
                  value: '%${o.correctRate.toStringAsFixed(1)}',
                ),
              ),
              SizedBox(
                width: 150,
                child: AiMetricTile(
                  label: 'Pomodoro oranı',
                  value: '%${o.pomodoroCompletionRate.toStringAsFixed(0)}',
                ),
              ),
            ],
          ),
          if (o.mostStudiedSubject != null) ...[
            const SizedBox(height: 12),
            Text('En çok çalışılan: ${o.mostStudiedSubject}'),
          ],
          if (o.topRecommendation != null) ...[
            const SizedBox(height: 12),
            Text(
              'Bugünün önerisi',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 6),
            Text(o.topRecommendation!.message),
          ],
        ],
      ),
    );
  }
}

class _RecommendationsCard extends StatelessWidget {
  const _RecommendationsCard({required this.state});

  final AiCoachLoaded state;

  @override
  Widget build(BuildContext context) {
    return AiSectionCard(
      title: 'Öneriler',
      icon: Icons.lightbulb_outline_rounded,
      child: state.recommendations.isEmpty
          ? const Text('Şu an gösterilecek öneri yok.')
          : Column(
              children: [
                for (final rec in state.recommendations)
                  AiRecommendationTile(recommendation: rec),
              ],
            ),
    );
  }
}

class _TrendsCard extends StatelessWidget {
  const _TrendsCard({required this.state});

  final AiCoachLoaded state;

  @override
  Widget build(BuildContext context) {
    final t = state.trends;
    return AiSectionCard(
      title: 'Trendler',
      icon: Icons.trending_up_rounded,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AiMetricTile(
            label: 'Bu hafta süre',
            value:
                '${t.weeklyStudyMinutes} dk (${formatDeltaPct(t.studyMinutesDeltaPct)})',
          ),
          const SizedBox(height: 10),
          AiMetricTile(
            label: 'Bu hafta soru',
            value:
                '${t.weeklyQuestions} (${formatDeltaPct(t.questionsDeltaPct)})',
          ),
          const SizedBox(height: 10),
          AiMetricTile(
            label: 'Bu ay süre',
            value: '${t.monthlyStudyMinutes} dk',
          ),
          if (t.dailySeries.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              'Günlük seri',
              style: Theme.of(context).textTheme.titleSmall,
            ),
            const SizedBox(height: 8),
            for (final point in t.dailySeries.take(7))
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '${point.label}: ${point.studyMinutes} dk · ${point.questionCount} soru',
                ),
              ),
          ],
        ],
      ),
    );
  }
}

class _PerformanceCard extends StatelessWidget {
  const _PerformanceCard({required this.state});

  final AiCoachLoaded state;

  @override
  Widget build(BuildContext context) {
    final p = state.performance;
    return AiSectionCard(
      title: 'Performans',
      icon: Icons.school_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Toplam ${p.totalQuestions} soru · Net ${p.totalNet.toStringAsFixed(1)}',
          ),
          const SizedBox(height: 8),
          Text(
            'Doğru %${p.correctRate.toStringAsFixed(1)} · Yanlış %${p.wrongRate.toStringAsFixed(1)}',
          ),
          if (p.subjectsByAccuracy.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              'Ders doğrulukları',
              style: Theme.of(context).textTheme.titleSmall,
            ),
            const SizedBox(height: 6),
            for (final m in p.subjectsByAccuracy.take(5))
              Text('${m.label}: ${m.value}${m.unit ?? ''}'),
          ],
        ],
      ),
    );
  }
}

class _ProductivityCard extends StatelessWidget {
  const _ProductivityCard({required this.state});

  final AiCoachLoaded state;

  @override
  Widget build(BuildContext context) {
    final p = state.productivity;
    return AiSectionCard(
      title: 'Verimlilik',
      icon: Icons.schedule_rounded,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('En verimli saat: ${formatHour(p.mostProductiveHour)}'),
          const SizedBox(height: 6),
          Text(
            'En verimli gün: ${p.mostProductiveWeekdayLabel ?? '—'}',
          ),
          const SizedBox(height: 6),
          Text('Streak: ${p.streakDays} gün'),
          const SizedBox(height: 6),
          Text('Son 14 günde boş gün: ${p.idleDaysLast14}'),
        ],
      ),
    );
  }
}
