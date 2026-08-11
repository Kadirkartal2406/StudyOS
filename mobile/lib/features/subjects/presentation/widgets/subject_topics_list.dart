import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_row.dart';
import '../../domain/entities/subject_hub_entity.dart';

/// Topics → Topic Work Surface — temiz liste satırları.
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
    final text = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Konular',
          style: text.titleLarge?.copyWith(
            fontWeight: FontWeight.w700,
            letterSpacing: -0.2,
          ),
        ),
        const SizedBox(height: AppSpacing.xxs),
        Text(
          items.isEmpty
              ? 'Bu ders için henüz konu kataloğu yok'
              : 'Çalışmak istediğin konuyu aç · ${topics.count} konu',
          style: text.bodyMedium?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        if (items.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.xl),
            child: Text(
              'Konu listesi boş',
              textAlign: TextAlign.center,
              style: text.bodyMedium?.copyWith(
                color: colorScheme.outline,
              ),
            ),
          )
        else
          ...items.map(
            (t) => StudyRow(
              title: t.topicName,
              subtitle: t.difficulty != null ? 'Zorluk ${t.difficulty}' : null,
              leading: Icons.play_circle_outline_rounded,
              leadingColor: AppColors.primary,
              onTap: () => context.push(
                '/subjects/$subjectCode/topics/${t.topicCode}',
              ),
            ),
          ),
      ],
    );
  }
}
