import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../domain/entities/subject_hub_entity.dart';
import '../../domain/subject_display_title.dart';

class SubjectHubHeader extends StatelessWidget {
  const SubjectHubHeader({super.key, required this.hub});

  final SubjectHubEntity hub;

  @override
  Widget build(BuildContext context) {
    final active = hub.activeExamType?.toUpperCase();
    final title = subjectDisplayTitle(
      subjectCode: hub.subject.subjectCode,
      subjectName: hub.subject.subjectName,
      section: hub.subject.section,
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          [
            if (active != null) 'Active: $active',
            hub.subject.subjectCode,
          ].join(' · '),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
      ],
    );
  }
}

class SubjectHubProgressCard extends StatelessWidget {
  const SubjectHubProgressCard({super.key, required this.progress});

  final SubjectHubProgress progress;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd.MM.yyyy');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'İlerleme',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: (progress.progressPct.clamp(0, 100)) / 100,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 12,
              runSpacing: 8,
              children: [
                _chip('${progress.progressPct.toStringAsFixed(0)}%'),
                _chip('Doğruluk %${progress.accuracy.toStringAsFixed(0)}'),
                _chip('${progress.totalQuestions} soru'),
                _chip('${progress.studyMinutes} dk'),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Son çalışma: ${progress.lastStudiedAt == null ? '—' : fmt.format(progress.lastStudiedAt!.toLocal())}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            Text(
              'Son tekrar: ${progress.lastRevisionAt == null ? '—' : fmt.format(progress.lastRevisionAt!.toLocal())}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label) => Chip(
        label: Text(label),
        visualDensity: VisualDensity.compact,
        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      );
}

class SubjectHubTodayCard extends StatelessWidget {
  const SubjectHubTodayCard({super.key, required this.today});

  final SubjectHubToday today;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: const Text('Bugün'),
        subtitle: Text(
          '${today.questionsSolved} soru · '
          '${today.completedPlanCount}/${today.planCount} plan · '
          '${today.studyMinutes} dk',
        ),
      ),
    );
  }
}

class SubjectHubRevisionCard extends StatelessWidget {
  const SubjectHubRevisionCard({
    super.key,
    required this.revision,
    required this.onOpen,
  });

  final SubjectHubRevision revision;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: const Text('Revision'),
        subtitle: Text(
          revision.dueToday + revision.overdue > 0
              ? 'Bugün ${revision.dueToday} · Geciken ${revision.overdue}'
                  '${revision.nextTitle != null ? ' · ${revision.nextTitle}' : ''}'
              : 'Bekleyen tekrar yok',
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: onOpen,
      ),
    );
  }
}

class SubjectHubPlannerCard extends StatelessWidget {
  const SubjectHubPlannerCard({
    super.key,
    required this.plans,
    required this.onOpenPlan,
    required this.onOpenPlanner,
  });

  final SubjectHubPlans plans;
  final VoidCallback onOpenPlan;
  final VoidCallback onOpenPlanner;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Plan',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              plans.todayCount == 0
                  ? 'Bugün bu dersten plan yok'
                  : '${plans.completedCount}/${plans.todayCount} tamamlandı'
                      '${plans.nextTitle != null ? ' · ${plans.nextTitle}' : ''}',
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                TextButton(onPressed: onOpenPlan, child: const Text('Study Plan')),
                TextButton(onPressed: onOpenPlanner, child: const Text('Planner')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class SubjectHubExamCard extends StatelessWidget {
  const SubjectHubExamCard({
    super.key,
    required this.exam,
    required this.onOpen,
  });

  final SubjectHubExamSummary exam;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    final subtitle = exam.available
        ? 'Ort. net ${exam.averageNet?.toStringAsFixed(1) ?? '—'} · '
            '${exam.examCount} deneme'
        : 'Deneme özeti yakında';
    return Card(
      child: ListTile(
        title: const Text('Exam'),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onOpen,
      ),
    );
  }
}

class SubjectHubAiCard extends StatelessWidget {
  const SubjectHubAiCard({
    super.key,
    required this.ai,
    required this.onOpenCoach,
  });

  final SubjectHubAi ai;
  final VoidCallback onOpenCoach;

  @override
  Widget build(BuildContext context) {
    final tip = ai.recommendation?.trim();
    final reason = ai.reason?.trim();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'AI',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                TextButton(onPressed: onOpenCoach, child: const Text('Koç')),
              ],
            ),
            Text(
              'Öneri',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 4),
            Text(
              tip == null || tip.isEmpty ? 'Bu ders için özel öneri yok.' : tip,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Sebep',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 4),
            Text(
              reason == null || reason.isEmpty
                  ? 'Sebep henüz yok.'
                  : reason,
            ),
            const SizedBox(height: 8),
            OutlinedButton(
              onPressed: ai.explainAvailable ? onOpenCoach : null,
              child: Text(
                ai.explainAvailable
                    ? 'Explain'
                    : ai.explainPlaceholder,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class SubjectHubResourcesCard extends StatelessWidget {
  const SubjectHubResourcesCard({
    super.key,
    required this.resources,
    required this.onOpen,
  });

  final SubjectHubResources resources;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: const Text('Resources'),
        subtitle: Text(
          resources.placeholder
              ? 'Kaynaklar yakında (subject_code bağlanacak)'
              : '${resources.count} kaynak',
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: onOpen,
      ),
    );
  }
}

class SubjectHubFlashcardsCard extends StatelessWidget {
  const SubjectHubFlashcardsCard({super.key, required this.flashcards});

  final SubjectHubFlashcards flashcards;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: const Text('Flashcards'),
        subtitle: Text(flashcards.message),
        enabled: flashcards.enabled,
      ),
    );
  }
}

class SubjectHubTopicsCard extends StatelessWidget {
  const SubjectHubTopicsCard({super.key, required this.topics});

  final SubjectHubTopics topics;

  @override
  Widget build(BuildContext context) {
    final items = topics.items;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Konular',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              items.isEmpty
                  ? 'Bu ders için henüz konu kataloğu yok'
                  : '${topics.count} konu',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (items.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...items.map(
                (t) => ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text(t.topicName),
                  subtitle: Text(t.topicCode),
                  trailing: t.difficulty == null
                      ? null
                      : Text('Z${t.difficulty}'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// RC2 M22.7 — SubjectHubActions (modül launcher) kaldırıldı.
// Work Surface merkez; hub yalnızca topic seçer.
