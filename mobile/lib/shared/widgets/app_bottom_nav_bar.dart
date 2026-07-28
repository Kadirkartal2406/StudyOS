import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Alt gezinme — RC3 Türkçe etiketler.
class AppBottomNavBar extends StatelessWidget {
  const AppBottomNavBar({super.key, required this.currentIndex});

  final int currentIndex;

  static const _destinations = [
    (icon: Icons.today_rounded, label: 'Bugün', route: '/dashboard'),
    (icon: Icons.menu_book_rounded, label: 'Derslerim', route: '/subjects'),
    (icon: Icons.calendar_today_outlined, label: 'Planım', route: '/study-plan'),
    (icon: Icons.map_outlined, label: 'Yolculuk', route: '/journey'),
    (icon: Icons.person_outline_rounded, label: 'Profil', route: '/profile'),
  ];

  void _handleTap(BuildContext context, int index) {
    if (index == currentIndex) return;
    context.go(_destinations[index].route);
  }

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: (i) => _handleTap(context, i),
      destinations: [
        for (final d in _destinations)
          NavigationDestination(icon: Icon(d.icon), label: d.label),
      ],
    );
  }
}
