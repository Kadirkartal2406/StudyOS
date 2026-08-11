import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_glass_button.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Tek Primary Action — tipografi + Glass CTA.
/// Decision / deepLink / explain API davranışı aynı.
class TodayNextActionCard extends ConsumerWidget {
  const TodayNextActionCard({super.key, required this.action});

  final NextActionEntity action;

  IconData get _actionIcon => switch (action.actionType) {
        'revision' => Icons.replay_rounded,
        'study_plan' => Icons.menu_book_rounded,
        'focus' => Icons.play_arrow_rounded,
        _ => Icons.play_arrow_rounded,
      };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;
    final isObserving = action.confidenceTone == 'low';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Şimdi yap',
          style: text.labelLarge?.copyWith(
            color: colorScheme.primary,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          action.title,
          style: text.headlineMedium?.copyWith(
            fontWeight: FontWeight.w700,
            height: 1.2,
            letterSpacing: -0.3,
          ),
        ),
        if (action.subtitle != null && action.subtitle!.isNotEmpty) ...[
          const SizedBox(height: AppSpacing.xs),
          Text(
            action.subtitle!,
            style: text.titleMedium?.copyWith(
              color: colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
        const SizedBox(height: AppSpacing.sm),
        Text(
          action.reason,
          style: text.bodyLarge?.copyWith(
            color: colorScheme.onSurfaceVariant,
            height: 1.45,
          ),
        ),
        if (isObserving) ...[
          const SizedBox(height: AppSpacing.xs),
          Text(
            'Gözlem modu — kesin teşhis yok',
            style: text.labelMedium?.copyWith(
              color: colorScheme.tertiary,
            ),
          ),
        ],
        const SizedBox(height: AppSpacing.lg),
        StudyGlassButton(
          label: action.ctaLabel,
          leadingIcon: _actionIcon,
          size: StudyGlassSize.large,
          onPressed: () => context.push(action.deepLinkHint),
        ),
        const SizedBox(height: AppSpacing.xs),
        Align(
          alignment: Alignment.center,
          child: TextButton(
            onPressed: () => _showExplanation(context, ref),
            child: const Text('Neden?'),
          ),
        ),
      ],
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
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
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
              StudyGlassButton(
                label: 'Tamam',
                leadingIcon: Icons.check_rounded,
                showTrailing: false,
                onPressed: () => Navigator.of(ctx).pop(),
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
