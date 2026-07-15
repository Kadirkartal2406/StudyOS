import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// Web GoRouter provider'ı.
/// Sprint-1.3'te auth guard ve gerçek ekranlar eklenecek.
final webAppRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    debugLogDiagnostics: true,
    routes: [
      GoRoute(
        path: '/',
        name: 'dashboard',
        builder: (context, state) => const _PlaceholderPage(title: 'Dashboard'),
      ),
      // Sprint-1.3'te eklenecek:
      // GoRoute(path: '/login', ...)
      // GoRoute(path: '/students', ...)
      // GoRoute(path: '/classes', ...)
    ],
  );
});

class _PlaceholderPage extends StatelessWidget {
  const _PlaceholderPage({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const FlutterLogo(size: 80),
            const SizedBox(height: 24),
            Text(
              'StudyOS — Kurumsal Panel',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 8),
            Text('$title — Sprint-1.1 kurulum tamamlandı'),
          ],
        ),
      ),
    );
  }
}
