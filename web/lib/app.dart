import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

/// StudyOS Kurumsal Web Paneli kök widget'ı.
class StudyOSWebApp extends ConsumerWidget {
  const StudyOSWebApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(webAppRouterProvider);

    return MaterialApp.router(
      title: 'StudyOS — Kurumsal Panel',
      theme: WebAppTheme.lightTheme(),
      darkTheme: WebAppTheme.darkTheme(),
      themeMode: ThemeMode.light,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
