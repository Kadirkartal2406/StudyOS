import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/widgets/app_empty_state.dart';
import '../../../../core/widgets/app_error_view.dart';
import '../../../../core/widgets/app_loading_skeleton.dart';
import '../../domain/entities/subject_hub_entity.dart';
import '../../domain/subject_display_title.dart';
import '../providers/subject_hub_provider.dart';
import '../widgets/subject_container_summary.dart';
import '../widgets/subject_hub_sections.dart';
import '../widgets/subject_topics_list.dart';

/// RC2 M22.7 — Subject Learning Container.
/// Tek amaç: Topic seç → Topic Work Surface. Modül launcher değildir.
class SubjectHubScreen extends ConsumerWidget {
  const SubjectHubScreen({super.key, required this.subjectCode});

  final String subjectCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(subjectHubProvider(subjectCode));

    return Scaffold(
      appBar: AppBar(
        title: async.maybeWhen(
          data: (hub) => Text(
            subjectDisplayTitle(
              subjectCode: hub.subject.subjectCode,
              subjectName: hub.subject.subjectName,
              section: hub.subject.section,
            ),
          ),
          orElse: () => const Text('Ders'),
        ),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => ref.invalidate(subjectHubProvider(subjectCode)),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: async.when(
        loading: () => const AppLoadingSkeleton(rows: 6),
        error: (e, _) => AppErrorView(
          message: e.toString(),
          onRetry: () => ref.invalidate(subjectHubProvider(subjectCode)),
        ),
        data: (hub) => _ContainerBody(
          hub: hub,
          onRefresh: () async {
            ref.invalidate(subjectHubProvider(subjectCode));
            await ref.read(subjectHubProvider(subjectCode).future);
          },
        ),
      ),
    );
  }
}

class _ContainerBody extends StatelessWidget {
  const _ContainerBody({
    required this.hub,
    required this.onRefresh,
  });

  final SubjectHubEntity hub;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          SubjectHubHeader(hub: hub),
          const SizedBox(height: 8),
          SubjectContainerSummary(
            progress: hub.progress,
            today: hub.today,
          ),
          const SizedBox(height: 20),
          if (hub.ai.recommendation != null || hub.ai.code != null) ...[
            _SubjectAiPriorityCard(
              ai: hub.ai,
              subjectCode: hub.subject.subjectCode,
            ),
            const SizedBox(height: 20),
          ],
          if (hub.topics.items.isEmpty)
            const AppEmptyState(
              title: 'Konu yok',
              message:
                  'Bu ders için Exam Intelligence konusu henüz yok. '
                  'Sınav / branch seçimini kontrol et.',
              icon: Icons.topic_outlined,
            )
          else
            SubjectTopicsList(
              topics: hub.topics,
              subjectCode: hub.subject.subjectCode,
            ),
        ],
      ),
    );
  }
}

class _SubjectAiPriorityCard extends StatelessWidget {
  const _SubjectAiPriorityCard({
    required this.ai,
    required this.subjectCode,
  });

  final SubjectHubAi ai;
  final String subjectCode;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final topicCode = ai.code;

    return Material(
      color: colorScheme.primaryContainer.withValues(alpha: 0.3),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: topicCode == null || topicCode.isEmpty
            ? null
            : () => context.push(
                  '/subjects/$subjectCode/topics/$topicCode',
                ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.auto_awesome, color: colorScheme.primary, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Öncelikli Konu',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: colorScheme.primary,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const Spacer(),
                  if (topicCode != null && topicCode.isNotEmpty)
                    Icon(Icons.chevron_right, color: colorScheme.primary),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                ai.recommendation ?? 'Bugün Çalış: ${ai.code}',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              if (ai.reason != null) ...[
                const SizedBox(height: 4),
                Text(
                  ai.reason!,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
