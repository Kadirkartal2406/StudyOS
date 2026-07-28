import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/goal_progress_entity.dart';
import '../providers/goal_provider.dart';
import '../providers/goal_state.dart';
import '../widgets/goal_card.dart';
import '../widgets/goal_progress_bar.dart';

class GoalsScreen extends ConsumerWidget {
  const GoalsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(goalProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Hedefler')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/goals/add'),
        child: const Icon(Icons.add),
      ),
      body: switch (state) {
        GoalInitial() || GoalLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        GoalError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.read(goalProvider.notifier).refresh(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        GoalLoaded(:final goals, :final progress, :final filterMode) => Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: SegmentedButton<GoalFilterMode>(
                  segments: const [
                    ButtonSegment(
                      value: GoalFilterMode.active,
                      label: Text('Aktif'),
                      icon: Icon(Icons.flag_outlined),
                    ),
                    ButtonSegment(
                      value: GoalFilterMode.progress,
                      label: Text('İlerleme'),
                      icon: Icon(Icons.trending_up_rounded),
                    ),
                    ButtonSegment(
                      value: GoalFilterMode.completed,
                      label: Text('Tamamlanan'),
                      icon: Icon(Icons.check_circle_outline),
                    ),
                  ],
                  selected: {filterMode},
                  onSelectionChanged: (set) {
                    ref.read(goalProvider.notifier).setFilter(set.first);
                  },
                ),
              ),
              if (filterMode == GoalFilterMode.progress)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Özet',
                            style: Theme.of(context)
                                .textTheme
                                .titleSmall
                                ?.copyWith(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Aktif: ${progress.activeCount} · '
                            'Tamamlanan: ${progress.completedCount} · '
                            'Ort. %${progress.averageProgress.toStringAsFixed(0)}',
                          ),
                          const SizedBox(height: 12),
                          GoalProgressBar(
                            progress: progress.averageProgress,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              Expanded(
                child: RefreshIndicator(
                  onRefresh: () => ref.read(goalProvider.notifier).refresh(),
                  child: filterMode == GoalFilterMode.progress
                      ? _ProgressList(progressItems: progress.items)
                      : goals.isEmpty
                          ? ListView(
                              children: const [
                                SizedBox(height: 120),
                                Center(child: Text('Henüz hedef yok')),
                              ],
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.all(16),
                              itemCount: goals.length,
                              separatorBuilder: (_, __) =>
                                  const SizedBox(height: 8),
                              itemBuilder: (context, index) =>
                                  GoalCard(goal: goals[index]),
                            ),
                ),
              ),
            ],
          ),
      },
    );
  }
}

class _ProgressList extends StatelessWidget {
  const _ProgressList({required this.progressItems});

  final List<GoalProgressItemEntity> progressItems;

  @override
  Widget build(BuildContext context) {
    if (progressItems.isEmpty) {
      return ListView(
        children: const [
          SizedBox(height: 120),
          Center(child: Text('İlerleme verisi yok')),
        ],
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: progressItems.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final item = progressItems[index];
        return Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () => context.push('/goals/${item.id}'),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 8),
                  GoalProgressBar(progress: item.progress),
                  const SizedBox(height: 6),
                  Text(
                    '${item.currentValue.toStringAsFixed(0)} / '
                    '${item.targetValue.toStringAsFixed(0)} · '
                    'Kalan: ${item.remaining.toStringAsFixed(0)}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
