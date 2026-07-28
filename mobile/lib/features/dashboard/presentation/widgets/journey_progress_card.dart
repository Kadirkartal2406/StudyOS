import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-3.0 K1 — Progress hero + soft onboarding CTA (D2)
class JourneyProgressCard extends StatelessWidget {
  const JourneyProgressCard({
    super.key,
    this.todayPct = 0,
    this.weekPct = 0,
    this.monthPct = 0,
    this.overallPct = 0,
    this.journeyStage = 'new_user',
    this.onboardingRequired = false,
    this.primaryExamType,
    this.daysRemaining,
    this.baselineLevel,
  });

  final double todayPct;
  final double weekPct;
  final double monthPct;
  final double overallPct;
  final String journeyStage;
  final bool onboardingRequired;
  final String? primaryExamType;
  final int? daysRemaining;
  final String? baselineLevel;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'Yolculuk',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                Chip(label: Text(_stageLabel(journeyStage))),
              ],
            ),
            if (onboardingRequired) ...[
              const SizedBox(height: 8),
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.flag_outlined),
                title: const Text('Profilini tamamla'),
                subtitle: const Text('AI doğru verilerle çalışsın'),
                trailing: TextButton(
                  onPressed: () => context.push('/onboarding'),
                  child: const Text('Kurulum'),
                ),
              ),
            ],
            if (primaryExamType != null) ...[
              const SizedBox(height: 8),
              Text(
                [
                  primaryExamType!.toUpperCase(),
                  if (daysRemaining != null) '$daysRemaining gün',
                  if (baselineLevel != null) 'seviye: $baselineLevel',
                ].join(' · '),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            const SizedBox(height: 12),
            _bar(context, 'Bugün', todayPct),
            _bar(context, 'Hafta', weekPct),
            _bar(context, 'Ay', monthPct),
            _bar(context, 'Genel', overallPct),
          ],
        ),
      ),
    );
  }

  Widget _bar(BuildContext context, String label, double pct) {
    final value = (pct.clamp(0, 100)) / 100.0;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(label),
              const Spacer(),
              Text('${pct.clamp(0, 100).toStringAsFixed(0)}%'),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(value: value),
        ],
      ),
    );
  }

  static String _stageLabel(String stage) {
    return switch (stage) {
      'new_user' => 'Yeni',
      'onboarding' => 'Kurulum',
      'learning' => 'Öğrenme',
      'consistent' => 'Düzenli',
      'advanced' => 'İleri',
      _ => stage,
    };
  }
}
