import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Alt gezinme — LOS § 13.2 Omurgası: Today · Topic (Derslerim) · Journey
class AppBottomNavBar extends StatelessWidget {
  const AppBottomNavBar({super.key, required this.currentIndex});

  final int currentIndex;

  static const _destinations = [
    (icon: Icons.today_rounded, label: 'Bugün', route: '/dashboard'),
    (icon: Icons.menu_book_rounded, label: 'Derslerim', route: '/subjects'),
    (icon: Icons.map_outlined, label: 'Yolculuk', route: '/journey'),
  ];

  void _handleTap(BuildContext context, int index) {
    if (index == currentIndex) return;
    context.go(_destinations[index].route);
  }

  @override
  Widget build(BuildContext context) {
    final validIndex = (currentIndex >= 0 && currentIndex < _destinations.length)
        ? currentIndex
        : 0;

    return NavigationBar(
      selectedIndex: validIndex,
      onDestinationSelected: (i) => _handleTap(context, i),
      destinations: [
        for (final d in _destinations)
          NavigationDestination(icon: Icon(d.icon), label: d.label),
      ],
    );
  }
}
