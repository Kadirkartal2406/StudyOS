import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/ds.dart';
import '../../data/topic_test_remote_datasource.dart';
import '../providers/topic_test_catalog_provider.dart';

/// Published catalog tests on the topic work surface (no Gemini).
class TopicTestsSection extends ConsumerWidget {
  const TopicTestsSection({
    super.key,
    required this.subjectCode,
    required this.topicCode,
    required this.topicName,
  });

  final String subjectCode;
  final String topicCode;
  final String topicName;

  Color _diffColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return const Color(0xFF2E7D32);
      case 'hard':
        return const Color(0xFFC62828);
      default:
        return const Color(0xFFF9A825);
    }
  }

  String _statusLabel(TopicTestListItem t) {
    if (t.userStatus == 'submitted') {
      if (t.accuracyPct != null) return '%${t.accuracyPct!.round()}';
      return 'Tamamlandı';
    }
    if (t.userStatus == 'in_progress') return 'Devam';
    return 'Başla';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = (subjectCode: subjectCode, topicCode: topicCode);
    final async = ref.watch(topicTestCatalogForTopicProvider(key));
    final q =
        'subject_code=${Uri.encodeComponent(subjectCode)}'
        '&topic_code=${Uri.encodeComponent(topicCode)}'
        '&topic_name=${Uri.encodeComponent(topicName)}';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(
          title: 'Konu Testleri',
          icon: Icons.fact_check_outlined,
        ),
        const SizedBox(height: AppSpacing.sm),
        async.when(
          loading: () => const SkeletonCard(height: 88),
          error: (_, __) => EmptyState(
            icon: Icons.fact_check_outlined,
            title: 'Testler yüklenemedi',
            message: 'Yenileyip tekrar dene.',
            ctaLabel: 'Yenile',
            onCta: () => ref.invalidate(topicTestCatalogForTopicProvider(key)),
          ),
          data: (catalog) {
            if (catalog.tests.isEmpty) {
              return const EmptyState(
                icon: Icons.hourglass_top_outlined,
                title: 'Bu konu için yeni testler hazırlanıyor.',
                message:
                    'Hazır testler yayınlandığında burada görünecek. '
                    'AI ile anlık üretim için Menü → Soru Üret kullan.',
              );
            }

            final byWeek = <String, List<TopicTestListItem>>{};
            for (final t in catalog.tests) {
              byWeek.putIfAbsent(t.weekId, () => []).add(t);
            }
            final weeks = byWeek.keys.toList()..sort((a, b) => b.compareTo(a));

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final week in weeks.take(4)) ...[
                  Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.xs),
                    child: Text(
                      week,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  ...byWeek[week]!.map((t) {
                    return MetricTile(
                      title: t.title,
                      subtitle:
                          '${t.questionCount} soru · ${_statusLabel(t)}',
                      leading: Container(
                        width: 10,
                        height: 10,
                        decoration: BoxDecoration(
                          color: _diffColor(t.difficulty),
                          shape: BoxShape.circle,
                        ),
                      ),
                      onTap: () => context.push(
                        '/topic-test-session?test_id=${t.id}&$q',
                      ),
                    );
                  }),
                  const SizedBox(height: AppSpacing.sm),
                ],
                TextButton(
                  onPressed: () => context.push('/topic-tests?$q'),
                  child: const Text('Tüm haftaları gör'),
                ),
              ],
            );
          },
        ),
      ],
    );
  }
}
