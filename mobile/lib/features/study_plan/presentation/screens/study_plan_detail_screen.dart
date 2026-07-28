import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../study_resources/domain/entities/study_resource_entity.dart';
import '../../../study_resources/presentation/providers/study_resource_provider.dart';
import '../../../study_resources/presentation/providers/study_resource_state.dart';
import '../../../study_resources/presentation/widgets/resource_card.dart';
import '../../domain/entities/study_plan_entity.dart';
import '../providers/study_plan_provider.dart';
import '../providers/study_plan_state.dart';

/// Hafif plan detay — Sprint-2.5 C1 (kaynaklar bölümü).
class StudyPlanDetailScreen extends ConsumerWidget {
  const StudyPlanDetailScreen({super.key, required this.planId});

  final String planId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final planState = ref.watch(studyPlanProvider);
    final ResourceKey resourceKey = (planId: planId, subjectCode: null, topicCode: null);
    final resourceState = ref.watch(studyResourceProvider(resourceKey));

    StudyPlanEntity? plan;
    if (planState is StudyPlanLoaded) {
      for (final p in planState.plans) {
        if (p.id == planId) {
          plan = p;
          break;
        }
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(plan?.title ?? 'Plan detay'),
        actions: [
          IconButton(
            tooltip: 'Düzenle',
            onPressed: () => context.push('/study-plan/edit/$planId'),
            icon: const Icon(Icons.edit_outlined),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/study-plan/$planId/resources'),
        icon: const Icon(Icons.library_books_outlined),
        label: const Text('Tüm kaynaklar'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
        children: [
          if (plan != null) ...[
            Text(plan.subject, style: Theme.of(context).textTheme.titleMedium),
            if (plan.topic != null) Text(plan.topic!),
            const SizedBox(height: 4),
            Text('Durum: ${plan.status.name}'),
            Text('Hedef soru: ${plan.targetQuestionCount}'),
            Text('Tahmini süre: ${plan.estimatedMinutes} dk'),
            const SizedBox(height: 16),
          ],
          Text('Kaynaklar', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          switch (resourceState) {
            StudyResourceLoading() || StudyResourceInitial() => const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: CircularProgressIndicator(),
                ),
              ),
            StudyResourceError(:final message) => Text(message),
            StudyResourceLoaded(:final items) => items.isEmpty
                ? const Text('Bu plana henüz kaynak eklenmedi.')
                : Column(
                    children: [
                      for (final r in items.take(5))
                        ResourceCard(
                          resource: r,
                          onOpen: () => ref
                              .read(studyResourceProvider(resourceKey).notifier)
                              .open(r.id),
                          onComplete: () => ref
                              .read(studyResourceProvider(resourceKey).notifier)
                              .setStatus(r.id, ResourceStatus.completed),
                          onDelete: () => ref
                              .read(studyResourceProvider(resourceKey).notifier)
                              .delete(r.id),
                        ),
                    ],
                  ),
          },
        ],
      ),
    );
  }
}
