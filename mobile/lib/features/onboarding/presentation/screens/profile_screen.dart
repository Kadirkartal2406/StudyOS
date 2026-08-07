import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../dashboard/presentation/providers/dashboard_state.dart';
import '../providers/first_run_phase_provider.dart';
import '../providers/learning_profile_provider.dart';

/// RC3 D4 — Gerçek profil hub (ayarlar ayrı).
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final dashState = ref.watch(dashboardProvider);
    final dash = dashState is DashboardLoaded ? dashState.dashboard : null;

    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.fullName,
      _ => 'Öğrenci',
    };
    final first = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final exam = (profile?.activeExamType ?? profile?.primaryExamType ?? '—')
        .toUpperCase();
    final target = profile?.examTargets.isNotEmpty == true
        ? profile!.examTargets.first
        : null;
    final reason = profile?.baselineReason ?? '';
    final coach = dash?.coachToday;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profil'),
        actions: [
          IconButton(
            tooltip: 'Ayarlar',
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.push('/settings'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 32,
                child: Text(
                  first.isNotEmpty ? first[0].toUpperCase() : '?',
                  style: const TextStyle(fontSize: 24),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    Text(
                      [
                        exam,
                        if (target?.branch != null) target!.branch,
                        if (target?.targetNet != null)
                          'Hedef ${target!.targetNet!.toStringAsFixed(0)} net',
                      ].whereType<String>().join(' · '),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    if (dash != null)
                      Text(
                        'Seri: ${dash.streakDays} gün',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                  ],
                ),
              ),
            ],
          ),
          if (dash != null) ...[
            const SizedBox(height: 20),
            Row(
              children: [
                _stat(context, '${dash.totalStudyMinutes ~/ 60}s', 'Süre'),
                _stat(context, '${dash.todayQuestionsSolved}', 'Bugün soru'),
                _stat(context, '${dash.totalPomodoros}', 'Odak'),
                _stat(
                  context,
                  '${dash.achievementTotalUnlocked}',
                  'Başarı',
                ),
              ],
            ),
          ],
          const SizedBox(height: 24),
          _tile(
            context,
            title: 'Hedefim',
            subtitle: '$exam${target?.targetNet == null ? '' : ' · ${target!.targetNet!.toStringAsFixed(0)} net'}',
            onTap: () => context.push('/goals'),
          ),
          _tile(
            context,
            title: 'Alışkanlıklarım',
            subtitle:
                'Günlük ${profile?.dailyStudyMinutes ?? '—'} dk · ${(profile?.availableDays.length ?? 0)} gün',
            onTap: () => context.push('/settings'),
          ),
          _tile(
            context,
            title: 'Güçlü / gelişim',
            subtitle: reason.isEmpty
                ? 'Sohbet ve seviye testiyle dolacak'
                : reason,
          ),
          _tile(
            context,
            title: 'AI beni nasıl görüyor',
            subtitle: coach?.body.isNotEmpty == true
                ? coach!.body
                : (coach?.headline.isNotEmpty == true
                    ? coach!.headline
                    : 'Seni tanıdıkça burada özet görünecek'),
          ),
          const Divider(height: 32),
          ListTile(
            leading: const Icon(Icons.auto_awesome_outlined),
            title: const Text('StudyOS’u yeniden tanı'),
            subtitle: const Text('Kişisel tanıtım turunu tekrar aç'),
            onTap: () async {
              await ref
                  .read(firstRunPhaseProvider.notifier)
                  .setPhase('tour');
              if (!context.mounted) return;
              context.go('/setup/tour');
            },
          ),
          ListTile(
            leading: const Icon(Icons.settings_outlined),
            title: const Text('Ayarlar'),
            onTap: () => context.push('/settings'),
          ),
        ],
      ),
    );
  }

  Widget _stat(BuildContext context, String v, String l) {
    return Expanded(
      child: Column(
        children: [
          Text(v, style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              )),
          Text(l, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }

  Widget _tile(
    BuildContext context, {
    required String title,
    required String subtitle,
    VoidCallback? onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle, maxLines: 3, overflow: TextOverflow.ellipsis),
        trailing: onTap == null ? null : const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
