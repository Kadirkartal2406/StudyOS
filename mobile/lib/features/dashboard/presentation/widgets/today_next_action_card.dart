import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../../../core/network/dio_client.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Alignment Sprint-1 — tek Primary Action (Decision Projection render).
/// İkinci CTA yoktur. Flutter karar vermez.
class TodayNextActionCard extends ConsumerWidget {
  const TodayNextActionCard({super.key, required this.action});

  final NextActionEntity action;

  IconData get _actionIcon => switch (action.actionType) {
        'revision' => Icons.replay,
        'study_plan' => Icons.menu_book,
        'focus' => Icons.play_circle,
        _ => Icons.play_circle,
      };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final isObserving = action.confidenceTone == 'low';

    return Card(
      elevation: 0,
      color: colorScheme.primaryContainer.withValues(alpha: 0.35),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(_actionIcon, size: 20, color: colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Şimdi yap',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: colorScheme.primary,
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              action.title,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            if (action.subtitle != null && action.subtitle!.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                action.subtitle!,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
            const SizedBox(height: 12),
            Text(
              action.reason,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            if (isObserving) ...[
              const SizedBox(height: 8),
              Text(
                'Gözlem modu — kesin teşhis yok',
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: colorScheme.tertiary,
                    ),
              ),
            ],
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: FilledButton(
                    onPressed: () => context.push(action.deepLinkHint),
                    child: Text(action.ctaLabel),
                  ),
                ),
                const SizedBox(width: 8),
                // Sprint 12 — "Neden?" butonu
                OutlinedButton(
                  onPressed: () => _showExplanation(context, ref),
                  child: const Text('Neden?'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _showExplanation(BuildContext context, WidgetRef ref) async {
    final dio = ref.read(dioClientProvider);
    try {
      showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (_) => const AlertDialog(
          content: SizedBox(
            height: 60,
            child: Center(child: CircularProgressIndicator()),
          ),
        ),
      );
      final resp = await dio.post<Map<String, dynamic>>(
        ApiEndpoints.aiExplain,
        data: {
          'context_type': 'next_action',
          'reason': action.reason,
          if (action.subjectCode != null) 'subject_code': action.subjectCode,
          if (action.topicCode != null) 'topic_code': action.topicCode,
        },
      );
      if (context.mounted) Navigator.of(context).pop();
      final data = resp.data?['data'];
      final explanation = data is Map
          ? (data['explanation'] ?? data['text'] ?? '').toString()
          : resp.data?['explanation']?.toString() ?? '';
      if (!context.mounted) return;
      showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (ctx) => Padding(
          padding: EdgeInsets.fromLTRB(
            24,
            24,
            24,
            MediaQuery.of(ctx).viewInsets.bottom + 24,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome_outlined, size: 18),
                  const SizedBox(width: 8),
                  Text(
                    'Neden bu öneri?',
                    style: Theme.of(ctx).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(explanation.isEmpty ? 'Açıklama üretilemedi.' : explanation),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: const Text('Tamam'),
                ),
              ),
            ],
          ),
        ),
      );
    } on DioException catch (e) {
      if (context.mounted) {
        Navigator.of(context).pop();
        final err = dioExceptionToAppException(e);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Açıklama alınamadı: ${err.message}')),
        );
      }
    }
  }
}
