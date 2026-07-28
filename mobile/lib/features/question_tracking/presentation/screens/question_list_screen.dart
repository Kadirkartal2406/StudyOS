import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../subjects/domain/subject_code_resolver.dart';
import '../providers/question_tracking_provider.dart';
import '../providers/question_tracking_state.dart';

class QuestionListScreen extends ConsumerStatefulWidget {
  const QuestionListScreen({super.key, this.subjectCode});

  /// Sprint-3.1.C — hub deep-link identity (not display name).
  final String? subjectCode;

  @override
  ConsumerState<QuestionListScreen> createState() => _QuestionListScreenState();
}

class _QuestionListScreenState extends ConsumerState<QuestionListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _applyFilter());
  }

  Future<void> _applyFilter() async {
    final code = widget.subjectCode;
    if (code == null || code.isEmpty) return;
    final profile = await ref.read(learningProfileProvider.future);
    final name = subjectNameForCode(profile, code);
    if (name != null) {
      await ref.read(questionListProvider.notifier).load(subject: name);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(questionListProvider);
    final code = widget.subjectCode;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          code == null || code.isEmpty ? 'Soru Takibi' : 'Sorular',
        ),
        actions: [
          if (code != null && code.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Center(
                child: Text(
                  code,
                  style: Theme.of(context).textTheme.labelSmall,
                ),
              ),
            ),
          IconButton(
            tooltip: 'İstatistikler',
            onPressed: () => context.push('/questions/statistics'),
            icon: const Icon(Icons.bar_chart_rounded),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/questions/add'),
        child: const Icon(Icons.add),
      ),
      body: switch (state) {
        QuestionListInitial() || QuestionListLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        QuestionListError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () =>
                      ref.read(questionListProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        QuestionListLoaded(:final page) => page.items.isEmpty
            ? const Center(child: Text('Henüz soru kaydı yok'))
            : RefreshIndicator(
                onRefresh: () async {
                  if (code == null || code.isEmpty) {
                    await ref.read(questionListProvider.notifier).load();
                  } else {
                    await _applyFilter();
                  }
                },
                child: ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: page.items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = page.items[index];
                    return Card(
                      child: ListTile(
                        title: Text(item.subject),
                        subtitle: Text(
                          '${item.topic ?? 'Konu yok'} · '
                          '${item.questionCount} soru · '
                          'Net ${item.netScore.toStringAsFixed(1)}',
                        ),
                        trailing: Text(
                          '${item.correctCount}/${item.wrongCount}/${item.blankCount}',
                        ),
                        onTap: () =>
                            context.push('/questions/${item.id}'),
                      ),
                    );
                  },
                ),
              ),
      },
    );
  }
}
