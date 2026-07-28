import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Sprint-3.1.B — Bugünkü görevler (plan / pomodoro / revision / hedef).
class DashboardTodayTasks extends StatelessWidget {
  const DashboardTodayTasks({
    super.key,
    required this.todayPlanCount,
    required this.completedPlanCount,
    required this.goalMinutes,
    required this.todayMinutes,
    required this.progressPercentage,
    required this.revisionDueToday,
    this.revisionNextTitle,
  });

  final int todayPlanCount;
  final int completedPlanCount;
  final int goalMinutes;
  final int todayMinutes;
  final double progressPercentage;
  final int revisionDueToday;
  final String? revisionNextTitle;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Bugünkü görevler',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 12),
            _TaskTile(
              icon: Icons.checklist_rounded,
              title: 'Study Plan',
              subtitle: todayPlanCount == 0
                  ? 'Bugün plan yok'
                  : '$completedPlanCount / $todayPlanCount tamamlandı',
              onTap: () => context.push('/study-plan'),
            ),
            _TaskTile(
              icon: Icons.timer_outlined,
              title: 'Pomodoro',
              subtitle: 'Odak oturumu başlat',
              onTap: () => context.push('/pomodoro'),
            ),
            _TaskTile(
              icon: Icons.replay_circle_filled_outlined,
              title: 'Revision',
              subtitle: revisionDueToday > 0
                  ? '$revisionDueToday tekrar · ${revisionNextTitle ?? ''}'
                      .trim()
                  : 'Bugün bekleyen tekrar yok',
              onTap: () => context.push('/revisions'),
            ),
            const Divider(height: 20),
            Text(
              'Bugünkü hedef',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 6),
            Text(
              '$todayMinutes / $goalMinutes dk',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: (progressPercentage.clamp(0, 100)) / 100,
            ),
          ],
        ),
      ),
    );
  }
}

class _TaskTile extends StatelessWidget {
  const _TaskTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      dense: true,
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}
