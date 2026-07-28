import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../adaptive_planner/presentation/providers/planner_provider.dart';
import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../exam_catalog/presentation/providers/exam_catalog_provider.dart';
import '../../../exam_tracking/presentation/providers/exam_provider.dart';
import '../../../goal_engine/presentation/providers/goal_provider.dart';
import '../../../journey/presentation/providers/journey_trends_provider.dart';
import '../../../onboarding/presentation/providers/active_exam_provider.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../onboarding/presentation/providers/onboarding_provider.dart';
import '../../../question_tracking/presentation/providers/question_tracking_provider.dart';
import '../../../revision/presentation/providers/revision_provider.dart';
import '../../../statistics/presentation/providers/statistics_provider.dart';
import '../../../study_plan/presentation/providers/study_plan_provider.dart';
import '../../../study_resources/presentation/providers/study_resource_provider.dart';
import '../../../subjects/presentation/providers/subject_hub_provider.dart';
import '../../../subjects/presentation/providers/topic_notebook_provider.dart';
import '../../../subjects/presentation/providers/topic_work_surface_provider.dart';

/// Duolingo-style Active Exam switcher — AppBar'da daima görünür.
/// Tek sınavda bile chip olarak gösterilir.
/// "Sınav Ekle" seçeneği → dialog.
class ActiveExamSwitcher extends ConsumerWidget {
  const ActiveExamSwitcher({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(activeExamControllerProvider);
    final options = state.availableExamTypes;
    final current =
        state.activeExamType ?? (options.isNotEmpty ? options.first : '?');
    final colorScheme = Theme.of(context).colorScheme;

    return PopupMenuButton<String>(
      enabled: !state.isChanging,
      tooltip: 'Sınav değiştir',
      position: PopupMenuPosition.under,
      onSelected: (value) {
        if (value == '__add__') {
          _showAddExamDialog(context, ref);
          return;
        }
        if (value != current) {
          ref.read(activeExamControllerProvider.notifier).setActiveExam(value);
          // M17.1 — switch sonrası tüm aktif-sınav yüzeylerini yenile
          ref.invalidate(learningProfileProvider);
          ref.invalidate(dashboardProvider);
          ref.invalidate(plannerProvider);
          ref.invalidate(goalProvider);
          ref.invalidate(questionListProvider);
          ref.invalidate(questionStatsProvider);
          ref.invalidate(examProvider);
          ref.invalidate(statisticsProvider);
          ref.invalidate(journeyTrendsProvider);
          ref.invalidate(studyPlanProvider);
          ref.invalidate(revisionProvider);
          ref.invalidate(subjectHubProvider);
          ref.invalidate(studyResourceProvider);
          ref.invalidate(topicNotebookProvider);
          ref.invalidate(topicWorkSurfaceProvider);
        }
      },
      itemBuilder: (context) => [
        for (final exam in options)
          PopupMenuItem<String>(
            value: exam,
            child: Row(
              children: [
                Icon(
                  exam == current
                      ? Icons.radio_button_checked_rounded
                      : Icons.radio_button_unchecked_rounded,
                  size: 18,
                  color: exam == current
                      ? colorScheme.primary
                      : colorScheme.outline,
                ),
                const SizedBox(width: 10),
                Text(
                  exam.toUpperCase(),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: exam == current
                            ? FontWeight.w700
                            : FontWeight.normal,
                      ),
                ),
                if (exam == state.primaryExamType) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 2,),
                    decoration: BoxDecoration(
                      color: colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      'Ana',
                      style: Theme.of(context)
                          .textTheme
                          .labelSmall
                          ?.copyWith(color: colorScheme.onPrimaryContainer),
                    ),
                  ),
                ],
              ],
            ),
          ),
        const PopupMenuDivider(),
        PopupMenuItem<String>(
          value: '__add__',
          child: Row(
            children: [
              Icon(Icons.add_circle_outline_rounded,
                  size: 18, color: colorScheme.primary,),
              const SizedBox(width: 10),
              Text(
                'Sınav Ekle',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: colorScheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ],
          ),
        ),
      ],
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        decoration: BoxDecoration(
          color: colorScheme.primaryContainer,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (state.isChanging)
              SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: colorScheme.onPrimaryContainer,
                ),
              )
            else
              Text(
                current.toUpperCase(),
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: colorScheme.onPrimaryContainer,
                    ),
              ),
            const SizedBox(width: 4),
            Icon(
              Icons.expand_more_rounded,
              size: 18,
              color: colorScheme.onPrimaryContainer,
            ),
          ],
        ),
      ),
    );
  }

  void _showAddExamDialog(BuildContext context, WidgetRef ref) {
    showDialog<void>(
      context: context,
      builder: (_) => _AddExamDialog(parentRef: ref),
    );
  }
}

// ── Add Exam Dialog ───────────────────────────────────────────────────────────

class _AddExamDialog extends ConsumerStatefulWidget {
  const _AddExamDialog({required this.parentRef});
  final WidgetRef parentRef;

  @override
  ConsumerState<_AddExamDialog> createState() => _AddExamDialogState();
}

class _AddExamDialogState extends ConsumerState<_AddExamDialog> {
  String? _exam; // null = henüz seçilmedi / options yükleniyor
  double _targetNet = 80;
  bool _saving = false;
  String? _error;

  /// Net max fallback (catalog name kullanılır; kod bilinmeyenler 100).
  double _netMaxFor(String exam) => switch (exam) {
        'tyt' => 120,
        'ayt' => 80,
        'yks' => 160,
        'lgs' => 90,
        'kpss' => 120,
        'ales' => 100,
        'dgs' => 120,
        'yds' => 80,
        'ags' => 100,
        'yokdil' => 80,
        _ => 100,
      };

  Future<void> _add(String examCode) async {
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await ref
          .read(learningProfileRepositoryProvider)
          .addExamTarget({
        'exam_type': examCode,
        'is_primary': false,
        'target_net': _targetNet,
      });
      widget.parentRef.invalidate(learningProfileProvider);
      widget.parentRef
          .read(activeExamControllerProvider.notifier)
          .refresh();
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final alreadySelected =
        profile?.examTargets.map((e) => e.examType).toSet() ?? <String>{};
    final catalogAsync = ref.watch(examCatalogExamsProvider);

    return catalogAsync.when(
      loading: () => const AlertDialog(
        title: Text('Sınav Ekle'),
        content: SizedBox(
          height: 64,
          child: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (e, _) => AlertDialog(
        title: const Text('Sınav Ekle'),
        content: Text('Katalog yüklenemedi: $e'),
        actions: [
          TextButton(
            onPressed: () => ref.invalidate(examCatalogExamsProvider),
            child: const Text('Tekrar Dene'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Kapat'),
          ),
        ],
      ),
      data: (exams) {
        final opts = exams
            .where((e) => !alreadySelected.contains(e.code))
            .toList();
        if (_exam != null && !opts.any((o) => o.code == _exam)) {
          _exam = null;
        }
        final currentExam =
            _exam ?? (opts.isNotEmpty ? opts.first.code : null);
        final netMax =
            currentExam != null ? _netMaxFor(currentExam) : 100.0;
        final safeNet = _targetNet.clamp(10.0, netMax);

        if (opts.isEmpty) {
          return AlertDialog(
            title: const Text('Sınav Ekle'),
            content: const Text('Tüm sınavlar zaten ekli.'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Tamam'),
              ),
            ],
          );
        }

        return AlertDialog(
          title: const Text('Sınav Ekle'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('Sınav seç (Exam Intelligence)'),
                const SizedBox(height: 8),
                DropdownButton<String>(
                  isExpanded: true,
                  value: currentExam,
                  items: opts
                      .map(
                        (o) => DropdownMenuItem(
                          value: o.code,
                          child: Text(o.name),
                        ),
                      )
                      .toList(),
                  onChanged: (v) => setState(() {
                    _exam = v;
                    _targetNet =
                        _targetNet.clamp(10.0, _netMaxFor(v ?? ''));
                  }),
                ),
                const SizedBox(height: 12),
                Text(
                  'Hedef net: ${safeNet.toStringAsFixed(0)} / ${netMax.toStringAsFixed(0)}',
                ),
                Slider(
                  value: safeNet,
                  min: 10,
                  max: netMax,
                  divisions: (netMax - 10).round().clamp(1, 9999),
                  label: safeNet.toStringAsFixed(0),
                  onChanged: (v) => setState(() => _targetNet = v),
                ),
                if (_error != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      _error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                        fontSize: 12,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: _saving ? null : () => Navigator.of(context).pop(),
              child: const Text('İptal'),
            ),
            FilledButton(
              onPressed: (_saving || currentExam == null)
                  ? null
                  : () => _add(currentExam),
              child: _saving
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Ekle'),
            ),
          ],
        );
      },
    );
  }
}
