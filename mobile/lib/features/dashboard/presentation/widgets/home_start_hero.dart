import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_glass_button.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../../../shared/widgets/study_liquid_glass.dart';
import '../../domain/entities/dashboard_entity.dart';

/// Primary start CTA + 3-stat strip — liquid glass Home hero.
class HomeStartHero extends ConsumerWidget {
  const HomeStartHero({
    super.key,
    required this.dashboard,
    this.action,
  });

  final DashboardEntity dashboard;
  final NextActionEntity? action;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final planned = dashboard.todayPlanCount;
    final progress = dashboard.dailyProgressPercentage.round().clamp(0, 100);
    final minutes = dashboard.todayStudyMinutes;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        StudyGlassButton(
          label: 'Çalışmaya Başla',
          leadingIcon: StudyIcons.play,
          trailingIcon: StudyIcons.next,
          size: StudyGlassSize.large,
          onPressed: action != null
              ? () => context.push(action!.deepLinkHint)
              : () => context.go('/subjects'),
        ),
        if (action != null) ...[
          const SizedBox(height: AppSpacing.xs),
          Center(
            child: TextButton(
              onPressed: () => _showExplanation(context, ref, action!),
              child: const Text('Neden?'),
            ),
          ),
        ],
        const SizedBox(height: AppSpacing.md),
        _StatsStrip(
          plannedLabel: planned > 0 ? '$planned Ders' : '—',
          progressLabel: '%$progress',
          durationLabel: '$minutes dk',
        ),
      ],
    );
  }

  Future<void> _showExplanation(
    BuildContext context,
    WidgetRef ref,
    NextActionEntity action,
  ) async {
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
              Text(
                action.title,
                style: Theme.of(ctx).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 12),
              Text(
                explanation.isEmpty ? action.reason : explanation,
              ),
              const SizedBox(height: 24),
              StudyGlassButton(
                label: 'Tamam',
                leadingIcon: StudyIcons.success,
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

class _StatsStrip extends StatelessWidget {
  const _StatsStrip({
    required this.plannedLabel,
    required this.progressLabel,
    required this.durationLabel,
  });

  final String plannedLabel;
  final String progressLabel;
  final String durationLabel;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final dark = Theme.of(context).brightness == Brightness.dark;

    Widget cell(String label, String value) {
      return Expanded(
        child: Column(
          children: [
            Text(
              label,
              style: text.labelMedium?.copyWith(
                color: scheme.onSurfaceVariant,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              value,
              style: text.titleSmall?.copyWith(
                color: scheme.primary,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      );
    }

    return StudyLiquidGlassCapsule(
      child: Row(
        children: [
          cell('Planlanan', plannedLabel),
          _divider(dark),
          cell('İlerleme', progressLabel),
          _divider(dark),
          cell('Süre', durationLabel),
        ],
      ),
    );
  }

  Widget _divider(bool dark) {
    return Container(
      width: 1,
      height: 28,
      color: dark
          ? Colors.white.withValues(alpha: 0.12)
          : AppColors.divider,
    );
  }
}
