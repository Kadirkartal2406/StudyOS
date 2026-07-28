import 'package:flutter/material.dart';

import '../../domain/entities/study_plan_entity.dart';
import '../../domain/entities/study_plan_status.dart';

/// Alignment Sprint-4 — Living Plan bloğu.
/// Primary: Complete / Skip. Edit/Delete = Override. Reorder yok.
class StudyCard extends StatelessWidget {
  const StudyCard({
    super.key,
    required this.plan,
    required this.isMutating,
    required this.onStart,
    required this.onStartStudy,
    required this.onComplete,
    required this.onSkip,
    required this.onEdit,
    required this.onDelete,
    this.onOpenDetail,
  });

  final StudyPlanEntity plan;
  final bool isMutating;
  final VoidCallback onStart;
  final VoidCallback onStartStudy;
  final VoidCallback onComplete;
  final VoidCallback onSkip;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final VoidCallback? onOpenDetail;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final statusInfo = _statusInfo(plan.status, colorScheme);
    final showTitleSecondary =
        plan.title.trim().isNotEmpty && plan.title.trim() != plan.displayLabel;

    return Card(
      margin: EdgeInsets.zero,
      child: InkWell(
        onTap: onOpenDetail,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 4,
                    height: 40,
                    decoration: BoxDecoration(
                      color: statusInfo.color,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          plan.displayLabel,
                          style: Theme.of(context)
                              .textTheme
                              .titleMedium
                              ?.copyWith(fontWeight: FontWeight.w700),
                        ),
                        if (showTitleSecondary) ...[
                          const SizedBox(height: 2),
                          Text(
                            plan.title,
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: colorScheme.onSurfaceVariant,
                                    ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  _StatusBadge(info: statusInfo),
                  PopupMenuButton<String>(
                    tooltip: 'Gelişmiş',
                    icon: const Icon(Icons.more_vert_rounded),
                    onSelected: (value) {
                      if (value == 'edit') onEdit();
                      if (value == 'delete') onDelete();
                    },
                    itemBuilder: (context) => const [
                      PopupMenuItem(
                        value: 'edit',
                        child: Text('Düzenle (Gelişmiş)'),
                      ),
                      PopupMenuItem(
                        value: 'delete',
                        child: Text('Kaldır (Gelişmiş)'),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                runSpacing: 6,
                children: [
                  if (plan.hasTimeRange)
                    _InfoChip(
                      icon: Icons.schedule_rounded,
                      label:
                          '${plan.plannedStartTime!.label}–${plan.plannedEndTime!.label}',
                    ),
                  _InfoChip(
                    icon: Icons.timer_outlined,
                    label: plan.status == StudyPlanStatus.completed
                        ? '${plan.completedMinutes}/${plan.estimatedMinutes} dk'
                        : '${plan.estimatedMinutes} dk',
                  ),
                  _InfoChip(
                    icon: Icons.quiz_outlined,
                    label: plan.status == StudyPlanStatus.completed
                        ? '${plan.completedQuestionCount}/${plan.targetQuestionCount} soru'
                        : '${plan.targetQuestionCount} soru',
                  ),
                ],
              ),
              if (!plan.status.isTerminal) ...[
                const SizedBox(height: 12),
                if (isMutating)
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 8),
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                else
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      // Primary — uygula
                      FilledButton.icon(
                        onPressed: onComplete,
                        icon: const Icon(Icons.check_rounded, size: 18),
                        label: const Text('Tamamla'),
                      ),
                      FilledButton.tonalIcon(
                        onPressed: onSkip,
                        icon: const Icon(Icons.skip_next_rounded, size: 18),
                        label: const Text('Atla'),
                      ),
                      // Secondary — çalışma aracı / status
                      OutlinedButton.icon(
                        onPressed: onStartStudy,
                        icon: const Icon(Icons.timer_outlined, size: 18),
                        label: const Text('Pomodoro'),
                      ),
                      if (plan.status == StudyPlanStatus.planned)
                        TextButton(
                          onPressed: onStart,
                          child: const Text('Başlat'),
                        ),
                    ],
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  _StatusInfo _statusInfo(StudyPlanStatus status, ColorScheme colorScheme) {
    return switch (status) {
      StudyPlanStatus.planned => _StatusInfo('Bekliyor', colorScheme.outline),
      StudyPlanStatus.inProgress =>
        _StatusInfo('Devam Ediyor', colorScheme.primary),
      StudyPlanStatus.completed =>
        const _StatusInfo('Tamamlandı', Colors.green),
      StudyPlanStatus.skipped => _StatusInfo('Atlandı', colorScheme.error),
    };
  }
}

class _StatusInfo {
  const _StatusInfo(this.label, this.color);
  final String label;
  final Color color;
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.info});

  final _StatusInfo info;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: info.color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        info.label,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: info.color,
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: colorScheme.onSurfaceVariant),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
      ],
    );
  }
}
