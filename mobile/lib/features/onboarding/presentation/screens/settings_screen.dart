import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../theme/presentation/providers/theme_preferences_provider.dart';

/// RC3 D4 — Ayarlar (profil’den ayrı).
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final prefs = ref.watch(themePreferencesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Ayarlar')),
      body: ListView(
        children: [
          const ListTile(
            title: Text('Görünüm'),
            dense: true,
          ),
          RadioListTile<ThemeMode>(
            title: const Text('Açık tema'),
            value: ThemeMode.light,
            groupValue: prefs.mode,
            onChanged: (v) {
              if (v != null) {
                ref.read(themePreferencesProvider.notifier).setMode(v);
              }
            },
          ),
          RadioListTile<ThemeMode>(
            title: const Text('Koyu tema'),
            value: ThemeMode.dark,
            groupValue: prefs.mode,
            onChanged: (v) {
              if (v != null) {
                ref.read(themePreferencesProvider.notifier).setMode(v);
              }
            },
          ),
          RadioListTile<ThemeMode>(
            title: const Text('Sistem teması'),
            value: ThemeMode.system,
            groupValue: prefs.mode,
            onChanged: (v) {
              if (v != null) {
                ref.read(themePreferencesProvider.notifier).setMode(v);
              }
            },
          ),
          const Divider(),
          const ListTile(
            title: Text('Vurgu rengi'),
            dense: true,
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                for (final c in ThemePreferences.accentOptions)
                  GestureDetector(
                    onTap: () => ref
                        .read(themePreferencesProvider.notifier)
                        .setAccent(c),
                    child: Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        color: c,
                        shape: BoxShape.circle,
                        border: Border.all(
                          width: prefs.accent.toARGB32() == c.toARGB32() ? 3 : 1,
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.notifications_outlined),
            title: const Text('Bildirimler'),
            onTap: () => context.push('/notification-settings'),
          ),
          ListTile(
            leading: const Icon(Icons.smart_toy_outlined),
            title: const Text('AI tercihleri'),
            onTap: () => context.push('/ai-settings'),
          ),
          ListTile(
            leading: const Icon(Icons.feedback_outlined),
            title: const Text('Geri bildirim'),
            onTap: () => context.push('/feedback'),
          ),
          ListTile(
            leading: const Icon(Icons.rate_review_outlined),
            title: const Text('Soru değerlendirme'),
            onTap: () => context.push('/qie-eval'),
          ),
          const Divider(),
          ListTile(
            leading: Icon(
              Icons.logout,
              color: Theme.of(context).colorScheme.error,
            ),
            title: Text(
              'Çıkış yap',
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
            onTap: () async {
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
    );
  }
}
