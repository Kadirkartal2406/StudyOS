import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../providers/question_tracking_provider.dart';

class QuestionDetailScreen extends ConsumerWidget {
  const QuestionDetailScreen({super.key, required this.recordId});

  final String recordId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(questionDetailProvider(recordId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Soru Detayı'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () => context.push('/questions/$recordId/edit'),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () async {
              final ok = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Silinsin mi?'),
                  content: const Text('Bu soru kaydı kalıcı olarak silinecek.'),
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
              await ref.read(questionListProvider.notifier).delete(recordId);
              ref.invalidate(dashboardProvider);
              ref.invalidate(questionStatsProvider);
              if (context.mounted) context.pop();
            },
          ),
        ],
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (e) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            ListTile(title: const Text('Ders'), subtitle: Text(e.subject)),
            ListTile(
              title: const Text('Konu'),
              subtitle: Text(e.topic ?? '—'),
            ),
            ListTile(
              title: const Text('Soru'),
              subtitle: Text(
                '${e.questionCount} (D:${e.correctCount} Y:${e.wrongCount} B:${e.blankCount})',
              ),
            ),
            ListTile(
              title: const Text('Net'),
              subtitle: Text(e.netScore.toStringAsFixed(2)),
            ),
            ListTile(
              title: const Text('Doğru oranı'),
              subtitle: Text('${e.correctRate.toStringAsFixed(1)}%'),
            ),
            ListTile(
              title: const Text('Süre'),
              subtitle: Text('${e.durationMinutes} dk'),
            ),
            ListTile(
              title: const Text('Sınav'),
              subtitle: Text(e.examType?.label ?? '—'),
            ),
            ListTile(
              title: const Text('Zorluk'),
              subtitle: Text(e.difficulty?.label ?? '—'),
            ),
            ListTile(
              title: const Text('Kaynak'),
              subtitle: Text(e.source?.label ?? '—'),
            ),
            if (e.note != null)
              ListTile(title: const Text('Not'), subtitle: Text(e.note!)),
          ],
        ),
      ),
    );
  }
}
