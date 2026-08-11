import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/study_glass_page.dart';
import '../../../../shared/widgets/study_glass_section.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../theme/presentation/providers/theme_preferences_provider.dart';

/// Ayarlar — liquid glass + design-system color swatches.
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final prefs = ref.watch(themePreferencesProvider);
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;

    return StudyGlassPage(
      title: const Text('Ayarlar'),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(
          AppSpacing.md,
          AppSpacing.sm,
          AppSpacing.md,
          AppSpacing.xxl,
        ),
        children: [
          StudyGlassSection(
            title: 'GÖRÜNÜM',
            children: [
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
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          StudyGlassSection(
            title: 'TASARIM RENKLERİ',
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                child: Text(
                  'Glass / Floating palette',
                  style: text.bodyMedium?.copyWith(
                    color: scheme.onSurfaceVariant,
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                child: Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    for (var i = 0; i < ThemePreferences.accentOptions.length; i++)
                      _AccentSwatch(
                        color: ThemePreferences.accentOptions[i],
                        label: ThemePreferences.accentLabels[i],
                        selected: prefs.accent.toARGB32() ==
                            ThemePreferences.accentOptions[i].toARGB32(),
                        onTap: () => ref
                            .read(themePreferencesProvider.notifier)
                            .setAccent(ThemePreferences.accentOptions[i]),
                      ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          StudyGlassSection(
            title: 'HESAP & UYGULAMA',
            children: [
              StudyMenuTile(
                title: 'Bildirimler',
                icon: StudyIcons.notifications,
                onTap: () => context.push('/notification-settings'),
              ),
              StudyMenuTile(
                title: 'AI tercihleri',
                icon: StudyIcons.aiSettings,
                onTap: () => context.push('/ai-settings'),
              ),
              StudyMenuTile(
                title: 'EAE Harita (Türkiye)',
                subtitle: 'Eğitim varlık motoru demo',
                icon: StudyIcons.maps,
                onTap: () => context.push('/eae-demo'),
              ),
              StudyMenuTile(
                title: 'Geri bildirim',
                icon: StudyIcons.feedback,
                onTap: () => context.push('/feedback'),
              ),
              StudyMenuTile(
                title: 'Soru değerlendirme',
                icon: StudyIcons.quiz,
                onTap: () => context.push('/qie-eval'),
              ),
              StudyMenuTile(
                title: 'Çıkış yap',
                icon: StudyIcons.logout,
                danger: true,
                onTap: () async {
                  await ref.read(authProvider.notifier).logout();
                  if (context.mounted) context.go('/login');
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _AccentSwatch extends StatelessWidget {
  const _AccentSwatch({
    required this.color,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final Color color;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: SizedBox(
        width: 72,
        child: Column(
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 160),
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                border: Border.all(
                  width: selected ? 3 : 1,
                  color: selected
                      ? Theme.of(context).colorScheme.onSurface
                      : Colors.white.withValues(alpha: 0.7),
                ),
                boxShadow: [
                  BoxShadow(
                    color: color.withValues(alpha: 0.35),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 6),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: text.labelSmall?.copyWith(
                fontWeight: selected ? FontWeight.w800 : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
