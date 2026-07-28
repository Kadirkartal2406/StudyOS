import 'package:flutter/material.dart';

/// Kart 2 — Bugünkü Çalışma: çalışma süresi, çözülen soru, çalışılan konu.
class TodayStudyCard extends StatelessWidget {
  const TodayStudyCard({
    super.key,
    required this.studyMinutes,
    required this.questionsSolved,
    required this.studiedTopic,
  });

  final int studyMinutes;
  final int questionsSolved;
  final String? studiedTopic;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.local_fire_department_rounded,
                  color: colorScheme.secondary,
                  size: 22,
                ),
                const SizedBox(width: 8),
                Text(
                  'Bugünkü Çalışma',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    icon: Icons.timer_outlined,
                    label: 'Çalışma Süresi',
                    value: '$studyMinutes dk',
                  ),
                ),
                Expanded(
                  child: _StatItem(
                    icon: Icons.check_circle_outline_rounded,
                    label: 'Çözülen Soru',
                    value: '$questionsSolved',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _StatItem(
              icon: Icons.menu_book_outlined,
              label: 'Çalışılan Konu',
              value: studiedTopic ?? 'Henüz konu çalışılmadı',
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  const _StatItem({required this.icon, required this.label, required this.value});

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: colorScheme.onSurfaceVariant),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
              Text(
                value,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
