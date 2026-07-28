import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-3.0.1 — Derslerim insight kartı.
class MySubjectsCard extends StatelessWidget {
  const MySubjectsCard({
    super.key,
    required this.subjectNames,
    this.primaryExamType,
    this.mostStudiedSubject,
    this.weakestSubject,
    this.longestIdleSubject,
    this.todayStudiedCount = 0,
  });

  final List<String> subjectNames;
  final String? primaryExamType;
  final String? mostStudiedSubject;
  final String? weakestSubject;
  final String? longestIdleSubject;
  final int todayStudiedCount;

  @override
  Widget build(BuildContext context) {
    final hasInsight = mostStudiedSubject != null ||
        weakestSubject != null ||
        longestIdleSubject != null ||
        todayStudiedCount > 0;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/subjects'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.menu_book_rounded,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Derslerim',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  if (primaryExamType != null)
                    Chip(
                      label: Text(primaryExamType!.toUpperCase()),
                      visualDensity: VisualDensity.compact,
                    ),
                  const Icon(Icons.chevron_right),
                ],
              ),
              const SizedBox(height: 8),
              if (subjectNames.isEmpty)
                Text(
                  'Kurulumdan sonra derslerin burada görünür',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                )
              else if (hasInsight) ...[
                _row('En çok çalışılan', mostStudiedSubject),
                _row('Hedefe en uzak', weakestSubject),
                _row('Uzun süredir çalışılmayan', longestIdleSubject),
                _row('Bugün çalışılan', '$todayStudiedCount ders'),
                const SizedBox(height: 4),
                Text(
                  '${subjectNames.length} ders · detay için dokun',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ] else ...[
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final name in subjectNames.take(6))
                      Chip(
                        label: Text(name),
                        visualDensity: VisualDensity.compact,
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '${subjectNames.length} ders · detay için dokun',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _row(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Expanded(
            child: Text(label, style: const TextStyle(fontSize: 13)),
          ),
          Flexible(
            child: Text(
              value ?? '—',
              textAlign: TextAlign.end,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
