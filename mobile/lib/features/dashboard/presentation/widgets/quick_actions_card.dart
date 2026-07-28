import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Demote kart — Today'de kullanılmaz (AS-1). Etiketler AS-4 Living Plan dilinde.
class QuickActionsCard extends StatelessWidget {
  const QuickActionsCard({super.key});

  static const _actions = [
    (icon: Icons.play_circle_fill_rounded, label: 'Çalışmaya Başla', route: '/'),
    (icon: Icons.timer_rounded, label: 'Pomodoro', route: '/pomodoro'),
    (icon: Icons.calendar_month_rounded, label: 'Bugünkü bloklar', route: '/study-plan'),
    (icon: Icons.flag_outlined, label: 'Hedefler', route: '/goals'),
    (icon: Icons.quiz_outlined, label: 'Soru Takibi', route: '/questions'),
    (icon: Icons.library_books_outlined, label: 'Kaynaklar', route: '/resources'),
    (icon: Icons.assignment_outlined, label: 'Denemeler', route: '/exams'),
    (icon: Icons.menu_book_outlined, label: 'Derslerim', route: '/subjects'),
    (icon: Icons.auto_awesome, label: 'Önerilen plan', route: '/planner'),
    (icon: Icons.replay_circle_filled_outlined, label: 'Tekrarlar', route: '/revisions'),
    (icon: Icons.emoji_events_outlined, label: 'Rozetler', route: '/achievements'),
    (icon: Icons.person_outline, label: 'Kurulum', route: '/onboarding'),
    (icon: Icons.auto_awesome_rounded, label: 'AI Koç', route: '/ai-chat'),
    (icon: Icons.history_rounded, label: 'Oturum Geçmişi', route: '/session-history'),
    (icon: Icons.bar_chart_rounded, label: 'Soru İstatistik', route: '/questions/statistics'),
  ];
  void _handleTap(BuildContext context, String label, String? route) {
    if (route != null) {
      context.push(route);
      return;
    }

    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text('$label — Yakında'),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
  }

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
                Icon(Icons.bolt_rounded, color: colorScheme.primary, size: 22),
                const SizedBox(width: 8),
                Text(
                  'Hızlı İşlemler',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 2.2,
              ),
              itemCount: _actions.length,
              itemBuilder: (context, index) {
                final action = _actions[index];
                return OutlinedButton.icon(
                  onPressed: () => _handleTap(context, action.label, action.route),
                  icon: Icon(action.icon, size: 20),
                  label: Text(
                    action.label,
                    overflow: TextOverflow.ellipsis,
                  ),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
