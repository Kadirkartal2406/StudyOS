import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/network/dio_client.dart';
import '../../domain/entities/dashboard_entity.dart';
import '../providers/dashboard_provider.dart';

/// LOS Hizalama — Living Plan Önerisi Banner'ı.
/// SUGGEST policy üretildiğinde Dashboard'da gösterilir.
/// Kullanıcı "Kabul Et" veya "Daha Sonra" seçebilir.
class LivingPlanSuggestionBanner extends ConsumerStatefulWidget {
  const LivingPlanSuggestionBanner({super.key, required this.suggestion});

  final LivingPlanSuggestionEntity suggestion;

  @override
  ConsumerState<LivingPlanSuggestionBanner> createState() =>
      _LivingPlanSuggestionBannerState();
}

class _LivingPlanSuggestionBannerState
    extends ConsumerState<LivingPlanSuggestionBanner> {
  bool _loading = false;

  Future<void> _handleAction(bool accept) async {
    setState(() => _loading = true);
    final dio = ref.read(dioClientProvider);
    try {
      final endpoint = accept ? '/living-plan/accept' : '/living-plan/reject';
      await dio.post<Map<String, dynamic>>(
        endpoint,
        data: {'draft_id': widget.suggestion.draftId},
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              accept
                  ? 'Plan önerisi kabul edildi ve bugüne eklendi.'
                  : 'Öneri ertelendi.',
            ),
          ),
        );
      }
      ref.read(dashboardProvider.notifier).retry();
    } on DioException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('İşlem gerçekleştirilemedi: ${e.message}')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 16),
      color: colorScheme.secondaryContainer.withValues(alpha: 0.4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: colorScheme.secondary.withValues(alpha: 0.3),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome_rounded,
                  size: 20,
                  color: colorScheme.secondary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Sistem Plan Önerisi',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        color: colorScheme.secondary,
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: colorScheme.secondary.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${widget.suggestion.estimatedMinutes} dk',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: colorScheme.secondary,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              widget.suggestion.displayTopic,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              widget.suggestion.reason,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: FilledButton.tonal(
                    onPressed: _loading ? null : () => _handleAction(true),
                    child: _loading
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Kabul Et'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton(
                    onPressed: _loading ? null : () => _handleAction(false),
                    child: const Text('Daha Sonra'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
