import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/utils/confidence_label.dart';
import '../../../../shared/widgets/ds.dart';
import '../../domain/entities/topic_notebook_entity.dart';
import '../../domain/entities/topic_work_surface_entity.dart';
import '../providers/topic_notebook_provider.dart';
import '../providers/topic_work_surface_provider.dart';
import '../widgets/explain_bottom_sheet.dart';

/// Sprint 16 — Topic Work Surface (vitrin ekranı polish).
class TopicWorkSurfaceScreen extends ConsumerWidget {
  const TopicWorkSurfaceScreen({
    super.key,
    required this.subjectCode,
    required this.topicCode,
  });

  final String subjectCode;
  final String topicCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = (subjectCode: subjectCode, topicCode: topicCode);
    final async = ref.watch(topicWorkSurfaceProvider(key));

    return Scaffold(
      appBar: AppBar(
        title: async.maybeWhen(
          data: (s) => Text(s.learningState.topicName),
          orElse: () => const Text('Konu'),
        ),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => ref.invalidate(topicWorkSurfaceProvider(key)),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 280),
        child: async.when(
          loading: () => ListView(
            key: const ValueKey('ws-loading'),
            padding: AppSpacing.pageWide,
            children: const [
              SkeletonCard(height: 140),
              SizedBox(height: AppSpacing.md),
              SkeletonCard(height: 88),
              SizedBox(height: AppSpacing.sm),
              SkeletonCard(height: 120),
            ],
          ),
          error: (e, _) => Center(
            key: const ValueKey('ws-error'),
            child: EmptyState(
              title: 'Work Surface yüklenemedi',
              message: '$e',
              ctaLabel: 'Tekrar Dene',
              onCta: () => ref.invalidate(topicWorkSurfaceProvider(key)),
            ),
          ),
          data: (surface) =>
              _WorkSurfaceBody(key: const ValueKey('ws-body'), surface: surface),
        ),
      ),
    );
  }
}

class _WorkSurfaceBody extends StatelessWidget {
  const _WorkSurfaceBody({super.key, required this.surface});

  final TopicWorkSurfaceEntity surface;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final state = surface.learningState;
    final action = surface.primaryAction;
    final intel = surface.intelligence;
    final q =
        'subject_code=${state.subjectCode}&topic_code=${state.topicCode}&topic_name=${Uri.encodeComponent(state.topicName)}';

    return ListView(
      padding: AppSpacing.pageWide,
      children: [
        Text(
          state.topicName,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        if (state.subjectName != null) ...[
          const SizedBox(height: AppSpacing.xxs),
          Text(
            state.subjectName!,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
          ),
        ],
        const SizedBox(height: AppSpacing.md),

        if (intel != null)
          IntelligenceCardWidget(
            headline: intel.headline,
            stars: intel.stars,
            confidenceChip: ConfidenceChip(
              level: intel.confidenceLevel,
              label: intel.confidenceLabel,
            ),
            rows: [
              if (intel.lastStudiedLabel != null)
                ('Son çalışma', intel.lastStudiedLabel!),
              if (intel.lastQuizLabel != null) ('Son Quiz', intel.lastQuizLabel!),
              if (intel.weakSpot != null) ('Zayıf nokta', intel.weakSpot!),
            ],
            suggestion: intel.suggestion,
          )
        else if (state.summaryLine != null)
          StudyCard(child: Text(state.summaryLine!)),

        if (surface.insights.isNotEmpty) ...[
          const SizedBox(height: AppSpacing.md),
          ...surface.insights.map(
            (c) => Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.xs),
              child: InsightCardWidget(
                message: c.message,
                tone: c.tone,
                onTap: c.deepLinkHint == null || c.deepLinkHint!.isEmpty
                    ? null
                    : () => context.push(c.deepLinkHint!),
              ),
            ),
          ),
        ],

        const SizedBox(height: AppSpacing.xl),
        const SectionHeader(title: 'Şimdi yap', icon: Icons.play_circle_outline),
        const SizedBox(height: AppSpacing.sm),
        PrimaryButton(
          label: action.title,
          onPressed: () => _openPrimaryTool(context, action),
        ),
        if (action.subtitle != null) ...[
          const SizedBox(height: AppSpacing.xs),
          Text(
            action.subtitle!,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
          ),
        ],
        const SizedBox(height: AppSpacing.xs),
        Text(
          action.reason,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: scheme.onSurfaceVariant,
              ),
        ),
        if (surface.coachBody != null && surface.coachBody!.isNotEmpty) ...[
          const SizedBox(height: AppSpacing.lg),
          const SectionHeader(
            title: 'Koç önerisi',
            icon: Icons.psychology_outlined,
          ),
          const SizedBox(height: AppSpacing.sm),
          StudyCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (surface.coachHeadline != null)
                  Text(
                    surface.coachHeadline!,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                const SizedBox(height: AppSpacing.xs),
                Text(surface.coachBody!),
              ],
            ),
          ),
        ],

        const SizedBox(height: AppSpacing.xl),
        const SectionHeader(title: 'Öğrenme geçmişi', icon: Icons.history),
        const SizedBox(height: AppSpacing.sm),
        if (surface.timeline.isNotEmpty)
          StudyCard(
            child: Column(
              children: surface.timeline
                  .take(8)
                  .map(
                    (e) => TimelineTile(
                      title: e.title,
                      subtitle: e.subtitle,
                      relativeLabel: e.relativeLabel,
                      icon: _timelineIcon(e.kind),
                      onTap: e.deepLinkHint == null || e.deepLinkHint!.isEmpty
                          ? null
                          : () => context.push(e.deepLinkHint!),
                    ),
                  )
                  .toList(),
            ),
          )
        else
          EmptyState(
            icon: Icons.timeline,
            title: 'Henüz geçmiş yok',
            message: 'Pomodoro veya quiz sonrası burada görünecek.',
            ctaLabel: 'Pomodoro başlat',
            onCta: () => context.go('/pomodoro?$q'),
          ),

        const SizedBox(height: AppSpacing.xl),
        const SectionHeader(title: 'Quizler', icon: Icons.quiz_outlined),
        const SizedBox(height: AppSpacing.sm),
        if (surface.quizHistory.isNotEmpty)
          ...surface.quizHistory.map((qItem) {
            final score = qItem.accuracyPct == null
                ? qItem.status
                : '%${qItem.accuracyPct!.round()}';
            return MetricTile(
              title: '${qItem.questionCount} Soru',
              subtitle: '$score · ${qItem.relativeLabel}',
              onTap: () {
                // READY stub/eski üretimleri yeniden açma — taze üret.
                // Submitted kayıtlar generation_id ile açılır.
                final submitted = qItem.status.toLowerCase() == 'submitted';
                final path = submitted
                    ? '/quiz-session?$q&generation_id=${qItem.id}'
                    : '/quiz-session?$q';
                context.push(path);
              },
            );
          })
        else
          EmptyState(
            icon: Icons.quiz_outlined,
            title: 'Henüz quiz çözmedin',
            message: 'İlk quizini çözerek sistemi seni tanımaya başlat.',
            ctaLabel: 'Soru üret',
            onCta: () => context.push('/quiz-session?$q'),
          ),

        const SizedBox(height: AppSpacing.xl),
        const SectionHeader(title: 'Kaynaklar', icon: Icons.menu_book_outlined),
        const SizedBox(height: AppSpacing.sm),
        if (surface.resources.isNotEmpty)
          ...surface.resources.take(6).map(
                (r) {
                  final health = r.knowledgeHealth;
                  final healthLabel = switch (health) {
                    'ready' || 'indexed' => 'Hazır',
                    'processing' => 'İşleniyor',
                    'needs_update' => 'Güncelleme gerekli',
                    'error' => 'Hata',
                    _ => null,
                  };
                  final parts = <String>[
                    r.intelligenceLabel,
                    if (healthLabel != null) healthLabel,
                    if (r.chunkCount > 0) '${r.chunkCount} parça',
                    if (r.citationCount > 0) '${r.citationCount} atıf',
                    if (r.usedByAi) 'AI kullanıyor',
                  ];
                  return MetricTile(
                    title: r.title,
                    subtitle: parts.join(' · '),
                    onTap: () => context.push('/resources?$q'),
                  );
                },
              )
        else
          EmptyState(
            icon: Icons.menu_book_outlined,
            title: 'Bu konuda kaynak yok',
            message: 'PDF, YouTube veya link ekleyerek Explain ve Notebook’u besle.',
            ctaLabel: 'Kaynak ekle',
            onCta: () => context.push('/resources?$q'),
          ),

        const SizedBox(height: AppSpacing.xl),
        const SectionHeader(title: 'Hızlı araçlar'),
        const SizedBox(height: AppSpacing.sm),
        Wrap(
          spacing: AppSpacing.xs,
          runSpacing: AppSpacing.xs,
          children: [
            TonalButton(
              label: 'Pomodoro',
              icon: Icons.timer_outlined,
              onPressed: () => context.go('/pomodoro?$q'),
            ),
            TonalButton(
              label: 'Quiz',
              icon: Icons.quiz_outlined,
              onPressed: () => context.push('/quiz-session?$q'),
            ),
            TonalButton(
              label: 'Soru Kaydı',
              icon: Icons.edit_note,
              onPressed: () => context.push('/questions?$q'),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),
        Wrap(
          spacing: AppSpacing.xs,
          runSpacing: AppSpacing.xs,
          children: surface.secondaryTools.map((tool) {
            return SecondaryButton(
              label: tool.label,
              onPressed: () => context.push(tool.deepLinkHint),
            );
          }).toList(),
        ),
        const SizedBox(height: AppSpacing.lg),
        _AiPanel(
          subjectCode: surface.learningState.subjectCode,
          topicCode: surface.learningState.topicCode,
        ),
        const SizedBox(height: AppSpacing.xl),
      ],
    );
  }

  IconData _timelineIcon(String kind) {
    return switch (kind) {
      'quiz' => Icons.quiz_outlined,
      'pomodoro' => Icons.timer_outlined,
      'revision' => Icons.replay,
      'explain' => Icons.auto_awesome,
      _ => Icons.history,
    };
  }

  void _openPrimaryTool(BuildContext context, TopicPrimaryActionEntity action) {
    final subject = action.subjectCode ?? surface.learningState.subjectCode;
    final topic = action.topicCode ?? surface.learningState.topicCode;
    final topicName = Uri.encodeComponent(surface.learningState.topicName);
    final q = 'subject_code=$subject&topic_code=$topic&topic_name=$topicName';
    final hint = action.toolHint;
    final path = switch (hint) {
      'revision' => '/revisions?$q',
      'pomodoro' => '/pomodoro?$q',
      _ => action.deepLinkHint.isNotEmpty ? action.deepLinkHint : '/pomodoro?$q',
    };
    if (path.contains('/topics/')) {
      context.go(hint == 'revision' ? '/revisions?$q' : '/pomodoro?$q');
      return;
    }
    context.push(path);
  }
}

class _AiPanel extends ConsumerWidget {
  const _AiPanel({required this.subjectCode, required this.topicCode});

  final String subjectCode;
  final String topicCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = (subjectCode: subjectCode, topicCode: topicCode);
    final notebookAsync = ref.watch(topicNotebookProvider(key));

    return notebookAsync.when(
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
      data: (notebook) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionHeader(
            title: notebook.displayTitle,
            icon: Icons.auto_awesome,
            subtitle: notebook.knowledgeReady
                ? '${notebook.knowledgeChunkCount} parça · ${notebook.knowledgeCitationCount} atıf'
                : 'Kaynaklar indexlenince özet burada',
          ),
          const SizedBox(height: AppSpacing.sm),
          _ConfidenceBadge(notebook: notebook),
          if (notebook.knowledgeSummary != null &&
              notebook.knowledgeSummary!.trim().isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              notebook.knowledgeSummary!,
              style: Theme.of(context).textTheme.bodyMedium,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
            ),
          ],
          const SizedBox(height: AppSpacing.sm),
          Text(
            notebook.resourceCount == 0
                ? 'Bu konuda henüz kaynak yok'
                : '${notebook.resourceCount} kaynak bağlı',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
          if (notebook.resources.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            ...notebook.resources.take(3).map(
                  (r) => Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.xs),
                    child: Text(
                      '· ${r.title}',
                      style: Theme.of(context).textTheme.bodySmall,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
          ],
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.xs,
            runSpacing: AppSpacing.xs,
            children: [
              TonalButton(
                label: 'Yenile',
                icon: Icons.refresh,
                onPressed: () async {
                  final dio = ref.read(dioClientProvider);
                  await dio.post(
                    ApiEndpoints.knowledgeReindex,
                    data: {
                      'subject_code': subjectCode,
                      'topic_code': topicCode,
                      'force': true,
                    },
                  );
                  ref.invalidate(topicNotebookProvider(key));
                },
              ),
              if (notebook.explainAvailable)
                TonalButton(
                  label: 'Açıkla',
                  icon: Icons.auto_awesome,
                  onPressed: () => ExplainBottomSheet.show(
                    context,
                    subjectCode,
                    topicCode,
                  ),
                ),
              if (notebook.quizAvailable)
                TonalButton(
                  label: 'Quiz (${notebook.quizDifficulty})',
                  icon: Icons.quiz_outlined,
                  onPressed: () => context.push(
                    '/quiz-session?subject_code=$subjectCode&topic_code=$topicCode',
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ConfidenceBadge extends StatelessWidget {
  const _ConfidenceBadge({required this.notebook});
  final TopicNotebookEntity notebook;

  @override
  Widget build(BuildContext context) {
    final label = ConfidenceLabel.fromLevel(notebook.confidenceLevel);
    return ConfidenceChip(
      level: notebook.confidenceLevel,
      label: '${label.text} · ${notebook.trend}',
    );
  }
}
