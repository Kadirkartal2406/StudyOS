import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/subject_hub_entity.dart';

/// Alignment Sprint-3 — Topics → Topic Work Surface.
class SubjectTopicsList extends StatelessWidget {
  const SubjectTopicsList({
    super.key,
    required this.topics,
    required this.subjectCode,
  });

  final SubjectHubTopics topics;
  final String subjectCode;

  @override
  Widget build(BuildContext context) {
    final items = topics.items;
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Konular',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          items.isEmpty
              ? 'Bu ders için henüz konu kataloğu yok'
              : 'Çalışmak istediğin konuyu aç · ${topics.count} konu',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: 12),
        if (items.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: Text(
              'Konu listesi boş',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: colorScheme.outline,
                  ),
            ),
          )
        else
          ...items.map((t) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Material(
                color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
                borderRadius: BorderRadius.circular(12),
                child: InkWell(
                  borderRadius: BorderRadius.circular(12),
                  onTap: () => context.push(
                    '/subjects/$subjectCode/topics/${t.topicCode}',
                  ),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 12,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.play_circle_outline_rounded,
                          color: colorScheme.primary,
                          size: 22,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                t.topicName,
                                style: Theme.of(context)
                                    .textTheme
                                    .titleSmall
                                    ?.copyWith(fontWeight: FontWeight.w700),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                t.topicCode,
                                style: Theme.of(context)
                                    .textTheme
                                    .labelSmall
                                    ?.copyWith(
                                      color: colorScheme.onSurfaceVariant,
                                    ),
                              ),
                            ],
                          ),
                        ),
                        if (t.difficulty != null)
                          Text(
                            'Z${t.difficulty}',
                            style: Theme.of(context).textTheme.labelMedium,
                          ),
                        Icon(
                          Icons.chevron_right_rounded,
                          color: colorScheme.outline,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          }),
      ],
    );
  }
}
