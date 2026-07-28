import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/achievement_entity.dart';
import '../providers/achievement_provider.dart';

class AchievementsScreen extends ConsumerWidget {
  const AchievementsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(achievementProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Rozetler'),
        actions: [
          IconButton(
            tooltip: 'Kontrol et',
            onPressed: () =>
                ref.read(achievementProvider.notifier).checkAndNotify(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: switch (state) {
        AchievementLoading() => const Center(child: CircularProgressIndicator()),
        AchievementError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                FilledButton(
                  onPressed: () => ref.read(achievementProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        AchievementLoaded(
          :final progress,
          :final unlocked,
          :final explanation,
          :final errorMessage,
        ) =>
          _Body(
            progress: progress,
            unlocked: unlocked,
            explanation: explanation,
            errorMessage: errorMessage,
          ),
      },
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({
    required this.progress,
    required this.unlocked,
    this.explanation,
    this.errorMessage,
  });

  final List<AchievementEntity> progress;
  final List<AchievementEntity> unlocked;
  final String? explanation;
  final String? errorMessage;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Açılan: ${unlocked.length} · Toplam puan: '
          '${unlocked.fold<int>(0, (s, e) => s + e.points)}',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        if (errorMessage != null) ...[
          const SizedBox(height: 8),
          Text(errorMessage!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
        ],
        if (explanation != null) ...[
          const SizedBox(height: 12),
          Text('Neden?', style: Theme.of(context).textTheme.titleMedium),
          Text(explanation!),
        ],
        const SizedBox(height: 16),
        Text('İlerleme', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        for (final item in progress)
          Card(
            child: ListTile(
              leading: Icon(
                item.unlocked ? Icons.emoji_events : Icons.emoji_events_outlined,
                color: item.unlocked
                    ? Theme.of(context).colorScheme.primary
                    : null,
              ),
              title: Text(item.title),
              subtitle: Text(
                '${item.category} · ${item.tier} · ${item.points}p\n'
                '${item.currentValue.toStringAsFixed(0)} / ${item.targetValue.toStringAsFixed(0)}'
                '${item.reason != null ? '\n${item.reason}' : ''}',
              ),
              isThreeLine: true,
              trailing: TextButton(
                onPressed: () =>
                    ref.read(achievementProvider.notifier).explain(item.id),
                child: const Text('Neden?'),
              ),
            ),
          ),
      ],
    );
  }
}
