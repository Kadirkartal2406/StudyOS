import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../domain/entities/goal_explain_entity.dart';
import '../providers/goal_provider.dart';
import '../widgets/goal_progress_bar.dart';

class GoalDetailScreen extends ConsumerStatefulWidget {
  const GoalDetailScreen({super.key, required this.goalId});

  final String goalId;

  @override
  ConsumerState<GoalDetailScreen> createState() => _GoalDetailScreenState();
}

class _GoalDetailScreenState extends ConsumerState<GoalDetailScreen> {
  GoalExplainEntity? _explain;
  var _explaining = false;

  Future<void> _loadExplain() async {
    setState(() => _explaining = true);
    try {
      final repo = ref.read(goalRepositoryProvider);
      final data = await repo.explain(widget.goalId);
      if (mounted) setState(() => _explain = data);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$e')),
        );
      }
    } finally {
      if (mounted) setState(() => _explaining = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(goalDetailProvider(widget.goalId));
    final dateFmt = DateFormat('dd.MM.yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hedef Detayı'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () => context.push('/goals/${widget.goalId}/edit'),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Silinsin mi?'),
                  content: const Text('Bu hedef kalıcı olarak silinecek.'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Vazgeç'),
                    ),
                    FilledButton(
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text('Sil'),
                    ),
                  ],
                ),
              );
              if (ok != true) return;
              await ref.read(goalProvider.notifier).delete(widget.goalId);
              ref.invalidate(dashboardProvider);
              if (context.mounted) context.pop();
            },
          ),
        ],
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (goal) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(
              goal.title,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            if (goal.description != null && goal.description!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(goal.description!),
            ],
            const SizedBox(height: 16),
            GoalProgressBar(progress: goal.progress, height: 12),
            const SizedBox(height: 8),
            Text(
              '%${goal.progress.toStringAsFixed(0)} · '
              '${goal.currentValue.toStringAsFixed(0)} / '
              '${goal.targetValue.toStringAsFixed(0)} · '
              'Kalan ${goal.remaining.toStringAsFixed(0)}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Tür'),
              subtitle: Text(goal.displayTypeLabel),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Periyot'),
              subtitle: Text(goal.period.label),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Öncelik'),
              subtitle: Text(goal.priority.label),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Durum'),
              subtitle: Text(goal.status.label),
            ),
            if (goal.examType != null)
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Sınav'),
                subtitle: Text(goal.examType!.toUpperCase()),
              ),
            if (goal.subject != null)
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Ders'),
                subtitle: Text(goal.subject!),
              ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Tarih aralığı'),
              subtitle: Text(
                '${DateFormat('dd.MM.yyyy').format(goal.startDate)} — '
                '${DateFormat('dd.MM.yyyy').format(goal.endDate)}',
              ),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Tahmini tamamlanma'),
              subtitle: Text(
                goal.estimatedCompletion ??
                    (goal.etaDays != null
                        ? '${goal.etaDays!.toStringAsFixed(0)} gün'
                        : '—'),
              ),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Son güncelleme'),
              subtitle: Text(dateFmt.format(goal.updatedAt.toLocal())),
            ),
            if (goal.whyCreated != null) ...[
              const SizedBox(height: 8),
              Text('Neden oluştu', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 4),
              Text(goal.whyCreated!),
            ],
            if (goal.progressSources.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                'İlerleme kaynakları',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                children: [
                  for (final s in goal.progressSources)
                    Chip(label: Text(s), visualDensity: VisualDensity.compact),
                ],
              ),
            ],
            if (goal.progressLog.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                'İlerleme geçmişi',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 8),
              ...goal.progressLog.reversed.take(10).map(
                    (e) => ListTile(
                      contentPadding: EdgeInsets.zero,
                      dense: true,
                      title: Text(e.source),
                      subtitle: Text(
                        [
                          if (e.note != null) e.note!,
                          if (e.delta != null) '+${e.delta}',
                          if (e.value != null) '= ${e.value}',
                          e.at,
                        ].join(' · '),
                      ),
                    ),
                  ),
            ],
            if (goal.milestonesReached.isNotEmpty)
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Kilometre taşları'),
                subtitle: Text(
                  goal.milestonesReached.map((m) => '%$m').join(', '),
                ),
              ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: _explaining ? null : _loadExplain,
              icon: _explaining
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.auto_awesome_outlined),
              label: const Text('AI ile açıkla'),
            ),
            if (_explain != null) ...[
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Açıklama',
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      const SizedBox(height: 8),
                      Text(_explain!.explanation),
                      const SizedBox(height: 12),
                      Text('Neden ilerledi: ${_explain!.whyProgressed}'),
                      const SizedBox(height: 6),
                      Text('Neden durdu: ${_explain!.whyStalled}'),
                      const SizedBox(height: 6),
                      Text('Nasıl tamamlanır: ${_explain!.howToComplete}'),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
