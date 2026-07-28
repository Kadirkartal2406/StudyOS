import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../subjects/domain/subject_code_resolver.dart';
import '../../domain/entities/revision_entity.dart';
import '../providers/revision_provider.dart';

class RevisionScreen extends ConsumerWidget {
  const RevisionScreen({super.key, this.subjectCode});

  /// Sprint-3.1.C — hub deep-link by subject_code.
  final String? subjectCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(revisionProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          subjectCode == null || subjectCode!.isEmpty
              ? 'Tekrarlar'
              : 'Tekrarlar',
        ),
        actions: [
          IconButton(
            tooltip: 'Kural motoru ile oluştur',
            onPressed: () => ref.read(revisionProvider.notifier).generate(),
            icon: const Icon(Icons.auto_awesome),
          ),
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => ref.read(revisionProvider.notifier).load(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddDialog(context, ref),
        child: const Icon(Icons.add),
      ),
      body: switch (state) {
        RevisionLoading() => const Center(child: CircularProgressIndicator()),
        RevisionError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                FilledButton(
                  onPressed: () => ref.read(revisionProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        RevisionLoaded(
          :final today,
          :final stats,
          :final explanation,
          :final errorMessage,
        ) =>
          _LoadedBody(
            today: _filterByProfile(ref, today),
            stats: stats,
            explanation: explanation,
            errorMessage: errorMessage,
            primaryExamType:
                ref.watch(learningProfileProvider).valueOrNull?.activeExamType ??
                    ref.watch(learningProfileProvider).valueOrNull?.primaryExamType,
            subjectCode: subjectCode,
          ),
      },
    );
  }

  List<RevisionItemEntity> _filterByProfile(
    WidgetRef ref,
    List<RevisionItemEntity> items,
  ) {
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final hubName = subjectNameForCode(profile, subjectCode);
    if (hubName != null) {
      final key = hubName.toLowerCase();
      return items.where((i) => i.subject.toLowerCase() == key).toList();
    }
    final names = profile?.subjectNames;
    if (names == null || names.isEmpty) return items;
    final allowed = names.map((e) => e.toLowerCase()).toSet();
    final filtered = items
        .where((i) => allowed.contains(i.subject.toLowerCase()))
        .toList();
    // Profil dersleriyle eşleşen yoksa tümünü göster (eski free-text kartlar)
    return filtered.isEmpty ? items : filtered;
  }

  Future<void> _showAddDialog(BuildContext context, WidgetRef ref) async {
    final profile = ref.read(learningProfileProvider).valueOrNull;
    final subjects = profile?.subjectNames ?? const <String>[];
    String? selectedSubject =
        subjects.isNotEmpty ? subjects.first : null;
    final subjectCtrl = TextEditingController(
      text: selectedSubject ?? '',
    );
    final titleCtrl = TextEditingController();
    final reasonCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Manuel tekrar kartı'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if ((profile?.activeExamType ?? profile?.primaryExamType) != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Sınav: ${(profile!.activeExamType ?? profile.primaryExamType)!.toUpperCase()}',
                      style: Theme.of(ctx).textTheme.labelLarge,
                    ),
                  ),
                ),
              if (subjects.isNotEmpty)
                DropdownButtonFormField<String>(
                  value: selectedSubject,
                  decoration: const InputDecoration(labelText: 'Ders'),
                  items: [
                    for (final s in subjects)
                      DropdownMenuItem(value: s, child: Text(s)),
                  ],
                  onChanged: (v) {
                    setLocal(() {
                      selectedSubject = v;
                      subjectCtrl.text = v ?? '';
                    });
                  },
                )
              else
                TextField(
                  controller: subjectCtrl,
                  decoration: const InputDecoration(labelText: 'Ders'),
                ),
              TextField(
                controller: titleCtrl,
                decoration: const InputDecoration(labelText: 'Başlık'),
              ),
              TextField(
                controller: reasonCtrl,
                decoration:
                    const InputDecoration(labelText: 'Gerekçe (opsiyonel)'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('İptal'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Ekle'),
            ),
          ],
        ),
      ),
    );
    if (ok == true && subjectCtrl.text.trim().isNotEmpty) {
      await ref.read(revisionProvider.notifier).addManual(
            subject: subjectCtrl.text.trim(),
            title: titleCtrl.text.trim().isEmpty
                ? '${subjectCtrl.text.trim()} tekrarı'
                : titleCtrl.text.trim(),
            reason: reasonCtrl.text.trim().isEmpty
                ? null
                : reasonCtrl.text.trim(),
          );
      invalidateLearningProfile(ref);
    }
  }
}

class _LoadedBody extends ConsumerWidget {
  const _LoadedBody({
    required this.today,
    required this.stats,
    this.explanation,
    this.errorMessage,
    this.primaryExamType,
    this.subjectCode,
  });

  final List<RevisionItemEntity> today;
  final RevisionStatisticsEntity stats;
  final String? explanation;
  final String? errorMessage;
  final String? primaryExamType;
  final String? subjectCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (subjectCode != null && subjectCode!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Chip(
              label: Text(subjectCode!),
              avatar: const Icon(Icons.menu_book_outlined, size: 16),
            ),
          ),
        if (primaryExamType != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Chip(label: Text('Sınav: ${primaryExamType!.toUpperCase()}')),
          ),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Özet',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Bugün ${stats.dueToday} · Gecikmiş ${stats.overdue} · '
                  'Hafta ${stats.dueThisWeek} · Aktif ${stats.totalActive}',
                ),
                Text(
                  'Ort. zorluk ${stats.averageDifficulty.toStringAsFixed(1)} · '
                  'Ease ${stats.averageEase.toStringAsFixed(2)}',
                ),
              ],
            ),
          ),
        ),
        if (errorMessage != null) ...[
          const SizedBox(height: 8),
          Text(
            errorMessage!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ],
        if (explanation != null) ...[
          const SizedBox(height: 12),
          Text('Neden?', style: Theme.of(context).textTheme.titleMedium),
          Text(explanation!),
        ],
        const SizedBox(height: 16),
        Text(
          'Bugünkü tekrarlar',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        if (today.isEmpty)
          const Card(
            child: ListTile(
              title: Text('Bugün due kart yok'),
              subtitle: Text('Kural motoru ile oluştur veya manuel ekle'),
            ),
          )
        else
          for (final item in today) _RevisionCard(item: item),
      ],
    );
  }
}

class _RevisionCard extends ConsumerWidget {
  const _RevisionCard({required this.item});

  final RevisionItemEntity item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final due = item.schedule?.dueAt;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              item.title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            Text(
              '${item.subject}'
              '${item.topic != null ? ' · ${item.topic}' : ''}'
              ' · Zorluk ${item.difficulty}/5'
              ' · ${item.sourceType}',
            ),
            if (due != null)
              Text('Due: ${DateFormat('dd.MM HH:mm').format(due.toLocal())}'),
            const SizedBox(height: 6),
            Text(
              item.reason,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [
                FilledButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).review(item.id, 'good'),
                  child: const Text('Good'),
                ),
                OutlinedButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).review(item.id, 'again'),
                  child: const Text('Again'),
                ),
                OutlinedButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).review(item.id, 'hard'),
                  child: const Text('Hard'),
                ),
                OutlinedButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).review(item.id, 'easy'),
                  child: const Text('Easy'),
                ),
                TextButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).skip(item.id),
                  child: const Text('Skip'),
                ),
                TextButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).postpone(item.id),
                  child: const Text('Ertele'),
                ),
                TextButton(
                  onPressed: () =>
                      ref.read(revisionProvider.notifier).explain(item.id),
                  child: const Text('Neden?'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
