import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../adaptive_planner/domain/entities/planner_entity.dart';
import '../../../adaptive_planner/presentation/providers/planner_provider.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../providers/first_run_phase_provider.dart';
import '../providers/learning_profile_provider.dart';

/// RC3 — Gün gün plan önizleme + onay / düzenle.
class SetupSystemSummaryScreen extends ConsumerStatefulWidget {
  const SetupSystemSummaryScreen({super.key});

  @override
  ConsumerState<SetupSystemSummaryScreen> createState() =>
      _SetupSystemSummaryScreenState();
}

class _SetupSystemSummaryScreenState
    extends ConsumerState<SetupSystemSummaryScreen> {
  bool _accepting = false;

  Future<void> _accept({bool force = false}) async {
    setState(() => _accepting = true);
    try {
      final ok =
          await ref.read(plannerProvider.notifier).accept(force: force);
      if (!mounted) return;
      if (!ok) {
        final state = ref.read(plannerProvider);
        final msg = state is PlannerPreview ? state.errorMessage : null;
        if (msg != null && msg.contains('Yine de')) {
          final forceOk = await showDialog<bool>(
            context: context,
            builder: (ctx) => AlertDialog(
              title: const Text('Çakışma'),
              content: Text(msg),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Vazgeç'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(ctx, true),
                  child: const Text('Yine de ekle'),
                ),
              ],
            ),
          );
          if (forceOk == true && mounted) {
            await _accept(force: true);
          }
        }
        return;
      }
      await ref.read(firstRunPhaseProvider.notifier).setPhase('today_plan');
      if (!mounted) return;
      context.go('/setup/today-plan');
    } finally {
      if (mounted) setState(() => _accepting = false);
    }
  }

  Future<void> _regenerate({
    double? targetNet,
    double? availableHours,
    List<int>? availableDays,
  }) async {
    final profile = ref.read(learningProfileProvider).valueOrNull;
    final exam =
        profile?.activeExamType ?? profile?.primaryExamType ?? 'kpss';
    final net = targetNet ??
        (profile?.examTargets.isNotEmpty == true
            ? (profile!.examTargets.first.targetNet ?? 90.0)
            : 90.0);
    final days = availableDays ??
        (profile?.availableDays.isNotEmpty == true
            ? profile!.availableDays
            : <int>[0, 1, 2, 3, 4]);
    final hours = availableHours ?? profile?.availableHours ?? 2.5;
    await ref.read(plannerProvider.notifier).generate(
          targetExam: exam,
          targetNet: net,
          availableDays: days,
          availableHours: hours,
        );
  }

  Future<void> _editPlanParams() async {
    final profile = ref.read(learningProfileProvider).valueOrNull;
    final netCtrl = TextEditingController(
      text: (profile?.examTargets.isNotEmpty == true
              ? (profile!.examTargets.first.targetNet ?? 90)
              : 90)
          .toStringAsFixed(0),
    );
    final hoursCtrl = TextEditingController(
      text: (profile?.availableHours ?? 2.5).toString(),
    );
    final selectedDays = <int>{
      ...(profile?.availableDays.isNotEmpty == true
          ? profile!.availableDays
          : <int>[0, 1, 2, 3, 4]),
    };
    const dayLabels = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setLocal) {
            return AlertDialog(
              title: const Text('Planı düzenle'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextField(
                      controller: netCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Hedef net (sınav geneli)',
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: hoursCtrl,
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: 'Günlük çalışma saati',
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Çalışma günleri',
                      style: Theme.of(ctx).textTheme.labelLarge,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      children: [
                        for (var i = 0; i < 7; i++)
                          FilterChip(
                            label: Text(dayLabels[i]),
                            selected: selectedDays.contains(i),
                            onSelected: (v) {
                              setLocal(() {
                                if (v) {
                                  selectedDays.add(i);
                                } else if (selectedDays.length > 1) {
                                  selectedDays.remove(i);
                                }
                              });
                            },
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: const Text('Vazgeç'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(ctx, true),
                  child: const Text('Yeniden oluştur'),
                ),
              ],
            );
          },
        );
      },
    );

    final net = double.tryParse(netCtrl.text.replaceAll(',', '.'));
    final hours = double.tryParse(hoursCtrl.text.replaceAll(',', '.'));
    netCtrl.dispose();
    hoursCtrl.dispose();
    if (ok != true || !mounted) return;
    await _regenerate(
      targetNet: net,
      availableHours: hours,
      availableDays: selectedDays.toList()..sort(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final planner = ref.watch(plannerProvider);
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: SafeArea(
        child: switch (planner) {
          PlannerLoading() => const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Plan hazırlanıyor…'),
                ],
              ),
            ),
          PlannerError(:final message) => _ErrorBody(
              message: message,
              onRetry: _regenerate,
            ),
          PlannerPreview(:final draft, :final errorMessage) => _PlanBody(
              name: name,
              draft: draft,
              errorMessage: errorMessage,
              accepting: _accepting,
              onAccept: () => _accept(),
              onEdit: _editPlanParams,
              onRegenerate: _regenerate,
            ),
          PlannerAccepted(:final draft) => _PlanBody(
              name: name,
              draft: draft,
              accepting: false,
              onAccept: () async {
                await ref
                    .read(firstRunPhaseProvider.notifier)
                    .setPhase('today_plan');
                if (!context.mounted) return;
                context.go('/setup/today-plan');
              },
              onEdit: _editPlanParams,
              acceptLabel: 'Bugünkü derslere geç',
            ),
          _ => _ErrorBody(
              message: 'Henüz plan yok. Yeniden oluşturalım.',
              onRetry: _regenerate,
            ),
        },
      ),
      backgroundColor: scheme.surface,
    );
  }
}

class _ErrorBody extends StatelessWidget {
  const _ErrorBody({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Spacer(),
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          FilledButton(onPressed: onRetry, child: const Text('Planı oluştur')),
          const Spacer(),
        ],
      ),
    );
  }
}

class _PlanBody extends StatelessWidget {
  const _PlanBody({
    required this.name,
    required this.draft,
    required this.onAccept,
    required this.onEdit,
    this.errorMessage,
    this.accepting = false,
    this.onRegenerate,
    this.acceptLabel = 'Planı onayla',
  });

  final String name;
  final PlannerDraftEntity draft;
  final String? errorMessage;
  final bool accepting;
  final VoidCallback onAccept;
  final VoidCallback onEdit;
  final VoidCallback? onRegenerate;
  final String acceptLabel;

  Map<DateTime, List<PlannerItemEntity>> _groupByDay() {
    final map = <DateTime, List<PlannerItemEntity>>{};
    for (final item in draft.items) {
      final d = DateTime(
        item.studyDate.year,
        item.studyDate.month,
        item.studyDate.day,
      );
      map.putIfAbsent(d, () => []).add(item);
    }
    final keys = map.keys.toList()..sort();
    return {for (final k in keys) k: map[k]!};
  }

  String _dayLabel(DateTime d) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final tomorrow = today.add(const Duration(days: 1));
    if (d == today) {
      return 'Bugün · ${DateFormat('d MMMM', 'tr_TR').format(d)}';
    }
    if (d == tomorrow) {
      return 'Yarın · ${DateFormat('d MMMM', 'tr_TR').format(d)}';
    }
    return DateFormat('EEEE · d MMMM', 'tr_TR').format(d);
  }

  @override
  Widget build(BuildContext context) {
    final byDay = _groupByDay();
    final exam = draft.targetExam.toUpperCase();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                name.isEmpty
                    ? 'Çalışma planın hazır'
                    : '$name, çalışma planın hazır',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                '$exam · hedef ~${draft.targetNet.toStringAsFixed(0)} · '
                'günde ~${draft.availableHours.toStringAsFixed(1)} saat',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
              if (draft.overviewReason != null &&
                  draft.overviewReason!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  draft.overviewReason!,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
              if (errorMessage != null) ...[
                const SizedBox(height: 8),
                Text(
                  errorMessage!,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
              ],
            ],
          ),
        ),
        Expanded(
          child: byDay.isEmpty
              ? const Center(child: Text('Plan maddesi yok'))
              : ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                  itemCount: byDay.length,
                  itemBuilder: (context, index) {
                    final day = byDay.keys.elementAt(index);
                    final items = byDay[day]!;
                    final totalMin = items.fold<int>(
                      0,
                      (s, e) => s + e.estimatedMinutes,
                    );
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    _dayLabel(day),
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleSmall
                                        ?.copyWith(fontWeight: FontWeight.w700),
                                  ),
                                ),
                                Text(
                                  '$totalMin dk',
                                  style: Theme.of(context).textTheme.labelLarge,
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            for (final item in items) ...[
                              Text(
                                item.subject +
                                    (item.topic != null && item.topic!.isNotEmpty
                                        ? ' · ${item.topic}'
                                        : ''),
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                [
                                  if (item.startTime != null &&
                                      item.endTime != null)
                                    '${item.startTime}–${item.endTime}',
                                  '${item.estimatedMinutes} dk',
                                  if (item.targetQuestionCount > 0)
                                    '${item.targetQuestionCount} soru',
                                  if (item.title.isNotEmpty) item.title,
                                ].join(' · '),
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                              if (item.reason.isNotEmpty)
                                Text(
                                  item.reason,
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.copyWith(
                                        color: Theme.of(context)
                                            .colorScheme
                                            .onSurfaceVariant,
                                      ),
                                ),
                              if (item != items.last) const SizedBox(height: 10),
                            ],
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              FilledButton(
                onPressed: accepting ? null : onAccept,
                child: accepting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Text(acceptLabel),
              ),
              const SizedBox(height: 8),
              OutlinedButton(
                onPressed: accepting ? null : onEdit,
                child: const Text('Düzenle'),
              ),
              if (onRegenerate != null)
                TextButton(
                  onPressed: accepting ? null : onRegenerate,
                  child: const Text('Yeniden oluştur'),
                ),
            ],
          ),
        ),
      ],
    );
  }
}
