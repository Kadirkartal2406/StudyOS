import 'package:flutter/material.dart';

import '../../../../core/theme/app_spacing.dart';

/// Home greeting — avatar · Merhaba · name · subtitle (theme-aware).
class HomeGlassGreeting extends StatelessWidget {
  const HomeGlassGreeting({
    super.key,
    required this.firstName,
    this.onAvatarTap,
    this.subtitle = 'Bugün ne çalışacaksın?',
  });

  final String firstName;
  final VoidCallback? onAvatarTap;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final name = firstName.trim().isEmpty ? 'Öğrenci' : firstName.trim();
    final initial = name.substring(0, 1).toUpperCase();

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Material(
          color: scheme.primary,
          shape: const CircleBorder(),
          child: InkWell(
            customBorder: const CircleBorder(),
            onTap: onAvatarTap,
            child: SizedBox(
              width: 48,
              height: 48,
              child: Center(
                child: Text(
                  initial,
                  style: text.titleLarge?.copyWith(
                    color: scheme.onPrimary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Merhaba,',
                style: text.titleMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '$name 👋',
                style: text.headlineMedium?.copyWith(
                  color: scheme.onSurface,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.4,
                  height: 1.15,
                ),
              ),
              const SizedBox(height: AppSpacing.xxs),
              Text(
                subtitle,
                style: text.titleSmall?.copyWith(
                  color: scheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
