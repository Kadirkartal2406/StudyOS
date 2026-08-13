import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_radius.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../../shared/widgets/study_floating_card.dart';
import '../../../../shared/widgets/study_glass_page.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../../../shared/widgets/study_liquid_glass.dart';
import '../../../../shared/widgets/study_row.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../theme/presentation/providers/theme_preferences_provider.dart';
import '../providers/dashboard_provider.dart';
import '../providers/dashboard_state.dart';

/// Menü — matches StudyOS Profile/Menu glass mockup (light + dark).
class MenuScreen extends ConsumerStatefulWidget {
  const MenuScreen({super.key});

  @override
  ConsumerState<MenuScreen> createState() => _MenuScreenState();
}

class _MenuScreenState extends ConsumerState<MenuScreen> {
  bool _focusMode = false;

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final prefs = ref.watch(themePreferencesProvider);
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final dashState = ref.watch(dashboardProvider);
    final dash = dashState is DashboardLoaded ? dashState.dashboard : null;

    final fullName = switch (auth) {
      AuthAuthenticated(:final user) => user.fullName,
      _ => 'Öğrenci',
    };
    final first = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final initial = first.trim().isEmpty
        ? '?'
        : first.trim().substring(0, 1).toUpperCase();

    final exam = (profile?.activeExamType ??
            profile?.primaryExamType ??
            dash?.activeExamType ??
            'YKS')
        .toUpperCase();
    final year = DateTime.now().year + (DateTime.now().month > 6 ? 1 : 0);
    final goalLine = '$exam · $year Hedefi';

    final minutes = dash?.todayStudyMinutes ?? 0;
    final streak = dash?.streakDays ?? 0;

    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;
    final themeLabel = switch (prefs.mode) {
      ThemeMode.light => 'Açık',
      ThemeMode.dark => 'Koyu',
      ThemeMode.system => 'Sistem',
    };

    return StudyGlassPage(
      actions: [
        IconButton(
          tooltip: 'Ayarlar',
          icon: Icon(StudyIcons.settings, color: scheme.onSurface),
          onPressed: () => context.push('/settings'),
        ),
      ],
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 4),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(
          AppSpacing.md,
          AppSpacing.xs,
          AppSpacing.md,
          AppSpacing.xxl,
        ),
        children: [
          // ── Account header ──
          StudyFloatingCard(
            onTap: () => context.push('/profile'),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: scheme.primary,
                  child: Text(
                    initial,
                    style: text.headlineSmall?.copyWith(
                      color: scheme.onPrimary,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        fullName,
                        style: text.titleLarge?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: scheme.onSurface,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 3,
                            ),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFBBF24).withValues(
                                alpha: 0.18,
                              ),
                              borderRadius: AppRadius.chip,
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.star_rounded,
                                  size: 14,
                                  color: Color(0xFFD97706),
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  'Premium',
                                  style: text.labelSmall?.copyWith(
                                    color: const Color(0xFFB45309),
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        goalLine,
                        style: text.bodyMedium?.copyWith(
                          color: scheme.onSurfaceVariant,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(StudyIcons.next, color: scheme.onSurfaceVariant),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),

          // ── Stat cards ──
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  label: 'Günlük Çalışma',
                  value: '$minutes dk',
                  child: CustomPaint(
                    size: const Size(double.infinity, 28),
                    painter: _MiniSparklinePainter(
                      color: scheme.primary,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: _StatCard(
                  label: 'Seri',
                  value: '$streak gün',
                  child: Icon(
                    Icons.local_fire_department_rounded,
                    color: AppColors.warning,
                    size: 28,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),

          // ── Çalışma ──
          _SectionLabel('ÇALIŞMA'),
          StudyFloatingCard(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
            child: Column(
              children: [
                _menuTile(
                  context,
                  title: 'Profilim',
                  icon: StudyIcons.profile,
                  color: AppColors.primary,
                  onTap: () => context.push('/profile'),
                ),
                _menuTile(
                  context,
                  title: 'Çalışma İstatistiklerim',
                  icon: StudyIcons.statistics,
                  color: AppColors.info,
                  onTap: () => context.push('/statistics'),
                ),
                _menuTile(
                  context,
                  title: 'Hedeflerim',
                  icon: StudyIcons.goal,
                  color: AppColors.warning,
                  onTap: () => context.push('/goals'),
                ),
                _menuTile(
                  context,
                  title: 'Deneme Sonuçlarım',
                  icon: StudyIcons.examResults,
                  color: AppColors.danger,
                  onTap: () => context.push('/exams'),
                ),
                _menuTile(
                  context,
                  title: 'Soru Üret',
                  icon: StudyIcons.quiz,
                  color: const Color(0xFF0EA5E9),
                  onTap: () => context.push('/soru-uret'),
                ),
                _menuTile(
                  context,
                  title: 'Notlarım',
                  icon: StudyIcons.memory,
                  color: const Color(0xFFEAB308),
                  onTap: () => context.push('/memory'),
                ),
                _menuTile(
                  context,
                  title: 'Kaynaklarım',
                  icon: StudyIcons.resources,
                  color: const Color(0xFF8B5CF6),
                  onTap: () => context.push('/resources'),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // ── Hızlı ──
          _SectionLabel('HIZLI'),
          StudyFloatingCard(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
            child: Column(
              children: [
                _menuTile(
                  context,
                  title: 'Bildirimler',
                  icon: StudyIcons.notifications,
                  color: AppColors.danger,
                  badge: '3',
                  onTap: () => context.push('/notification-settings'),
                ),
                _menuTile(
                  context,
                  title: 'Planım',
                  icon: StudyIcons.plan,
                  color: AppColors.primary,
                  onTap: () => context.go('/study-plan'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.md,
                    vertical: AppSpacing.sm,
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: AppColors.primaryLight.withValues(alpha: 0.14),
                          borderRadius: AppRadius.chip,
                        ),
                        child: const Icon(
                          StudyIcons.focus,
                          color: AppColors.primaryLight,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      Expanded(
                        child: Text(
                          'Odak Modu',
                          style: text.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      Switch.adaptive(
                        value: _focusMode,
                        activeThumbColor: scheme.primary,
                        onChanged: (v) {
                          setState(() => _focusMode = v);
                          if (v) context.go('/pomodoro');
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // ── Uygulama ──
          _SectionLabel('UYGULAMA'),
          StudyFloatingCard(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
            child: Column(
              children: [
                _menuTile(
                  context,
                  title: 'Tema',
                  icon: Icons.contrast_rounded,
                  color: scheme.onSurfaceVariant,
                  trailing: Text(
                    themeLabel,
                    style: text.bodyMedium?.copyWith(
                      color: scheme.onSurfaceVariant,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  onTap: () => context.push('/settings'),
                ),
                _menuTile(
                  context,
                  title: 'Dil',
                  icon: Icons.language_rounded,
                  color: AppColors.info,
                  trailing: Text(
                    'Türkçe',
                    style: text.bodyMedium?.copyWith(
                      color: scheme.onSurfaceVariant,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  onTap: () {},
                ),
                _menuTile(
                  context,
                  title: 'Yardım & Destek',
                  icon: StudyIcons.help,
                  color: AppColors.success,
                  onTap: () => context.push('/feedback'),
                ),
                _menuTile(
                  context,
                  title: 'Hakkında',
                  icon: StudyIcons.info,
                  color: AppColors.primary,
                  onTap: () => _showAbout(context),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // ── Logout ──
          StudyLiquidGlass(
            intensity: LiquidGlassIntensity.strong,
            tint: AppColors.errorSoft,
            borderRadius: AppRadius.surface,
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.lg,
              vertical: AppSpacing.md,
            ),
            onTap: () => _confirmLogout(context),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(StudyIcons.logout, color: scheme.error),
                const SizedBox(width: AppSpacing.sm),
                Text(
                  'Çıkış Yap',
                  style: text.titleMedium?.copyWith(
                    color: scheme.error,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _menuTile(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
    String? badge,
    Widget? trailing,
  }) {
    return StudyRow(
      title: title,
      leading: icon,
      leadingColor: color,
      trailing: badge != null
          ? Container(
              constraints: const BoxConstraints(minWidth: 22, minHeight: 22),
              padding: const EdgeInsets.symmetric(horizontal: 6),
              alignment: Alignment.center,
              decoration: const BoxDecoration(
                color: AppColors.danger,
                shape: BoxShape.circle,
              ),
              child: Text(
                badge,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                ),
              ),
            )
          : trailing,
      onTap: onTap,
    );
  }

  Future<void> _confirmLogout(BuildContext context) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) {
        final scheme = Theme.of(ctx).colorScheme;
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: AppRadius.surface),
          title: Column(
            children: [
              Icon(StudyIcons.logout, color: scheme.error, size: 36),
              const SizedBox(height: 12),
              const Text('Çıkış yapmak istiyor musun?', textAlign: TextAlign.center),
            ],
          ),
          actionsAlignment: MainAxisAlignment.center,
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('İptal'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(backgroundColor: scheme.error),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Çıkış Yap'),
            ),
          ],
        );
      },
    );
    if (ok == true && mounted) {
      await ref.read(authProvider.notifier).logout();
    }
  }

  void _showAbout(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StudyLiquidGlass(
        intensity: LiquidGlassIntensity.strong,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        padding: const EdgeInsets.fromLTRB(24, 12, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Theme.of(ctx).colorScheme.onSurfaceVariant.withValues(
                      alpha: 0.35,
                    ),
                borderRadius: BorderRadius.circular(99),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Hakkında',
              style: Theme.of(ctx).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'StudyOS · v0.24',
              style: Theme.of(ctx).textTheme.bodyLarge?.copyWith(
                    color: Theme.of(ctx).colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel(this.label);
  final String label;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(
        left: AppSpacing.xxs,
        bottom: AppSpacing.sm,
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.4,
            ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.label,
    required this.value,
    required this.child,
  });

  final String label;
  final String value;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return StudyLiquidGlass(
      intensity: LiquidGlassIntensity.strong,
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: text.labelMedium?.copyWith(
              color: scheme.onSurfaceVariant,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: text.headlineSmall?.copyWith(
              fontWeight: FontWeight.w800,
              color: scheme.onSurface,
              letterSpacing: -0.4,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          SizedBox(height: 28, width: double.infinity, child: child),
        ],
      ),
    );
  }
}

class _MiniSparklinePainter extends CustomPainter {
  _MiniSparklinePainter({required this.color});
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final path = Path()
      ..moveTo(0, size.height * 0.7)
      ..quadraticBezierTo(
        size.width * 0.2,
        size.height * 0.9,
        size.width * 0.35,
        size.height * 0.45,
      )
      ..quadraticBezierTo(
        size.width * 0.55,
        size.height * 0.1,
        size.width * 0.7,
        size.height * 0.4,
      )
      ..quadraticBezierTo(
        size.width * 0.85,
        size.height * 0.65,
        size.width,
        size.height * 0.25,
      );
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _MiniSparklinePainter oldDelegate) =>
      oldDelegate.color != color;
}
