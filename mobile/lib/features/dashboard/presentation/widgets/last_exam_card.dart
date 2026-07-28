import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

/// Sprint-2.6 L1 — Son deneme özeti kartı.
class LastExamCard extends StatelessWidget {
  const LastExamCard({
    super.key,
    this.title,
    this.net,
    this.deltaNet,
    this.examDate,
    this.aiSummary,
  });

  final String? title;
  final double? net;
  final double? deltaNet;
  final DateTime? examDate;
  final String? aiSummary;

  @override
  Widget build(BuildContext context) {
    if (title == null) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.assignment_outlined),
          title: const Text('Henüz deneme yok'),
          trailing: TextButton(
            onPressed: () => context.push('/exams/add'),
            child: const Text('Ekle'),
          ),
        ),
      );
    }

    final delta = deltaNet;
    final deltaLabel = delta == null
        ? ''
        : ' · ${delta >= 0 ? '+' : ''}${delta.toStringAsFixed(1)}';
    final dateLabel =
        examDate == null ? '' : DateFormat('dd.MM.yyyy').format(examDate!);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.assignment_turned_in_outlined,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Son deneme',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () => context.push('/exams'),
                  child: const Text('Tümü'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(title!),
            Text(
              'Net ${(net ?? 0).toStringAsFixed(1)}$deltaLabel'
              '${dateLabel.isEmpty ? '' : ' · $dateLabel'}',
            ),
            if (aiSummary != null && aiSummary!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                aiSummary!,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
