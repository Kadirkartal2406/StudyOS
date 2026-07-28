import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/notification_settings_provider.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../../core/platform/platform_providers.dart';

class NotificationSettingsScreen extends ConsumerStatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  ConsumerState<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends ConsumerState<NotificationSettingsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(notificationSettingsProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(notificationSettingsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Profil & Ayarlar')),
      body: switch (state) {
        NotificationSettingsInitial() || NotificationSettingsLoading() =>
          const Center(child: CircularProgressIndicator()),
        NotificationSettingsError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () =>
                      ref.read(notificationSettingsProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        NotificationSettingsLoaded(
          :final settings,
          :final notificationsAllowed,
        ) =>
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (notificationsAllowed == false)
                Card(
                  color: Theme.of(context).colorScheme.errorContainer,
                  child: ListTile(
                    title: const Text('Bildirim izni kapalı'),
                    subtitle: const Text(
                      'Pomodoro ve hatırlatmalar için izin verin.',
                    ),
                    trailing: TextButton(
                      onPressed: () async {
                        final platform = ref.read(platformServiceProvider);
                        final ok =
                            await platform.requestNotificationPermission();
                        if (!ok) {
                          await platform.openSystemNotificationSettings();
                        }
                        await ref
                            .read(notificationSettingsProvider.notifier)
                            .load();
                      },
                      child: const Text('İzin Ver'),
                    ),
                  ),
                ),
              SwitchListTile(
                title: const Text('Pomodoro Bildirimleri'),
                value: settings.pomodoroEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('pomodoro_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Uzun Mola'),
                value: settings.longBreakEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('long_break_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Günlük Hatırlatma'),
                value: settings.dailyReminderEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('daily_reminder_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Günlük Hedef Bildirimi'),
                value: settings.dailyGoalEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('daily_goal_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Streak Hatırlatma'),
                value: settings.streakReminderEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('streak_reminder_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Rozet Bildirimleri'),
                value: settings.achievementNotificationsEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('achievement_notifications_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Widget Otomatik Güncelle'),
                value: settings.widgetAutoUpdateEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('widget_auto_update_enabled', v),
              ),
              SwitchListTile(
                title: const Text('Sessiz Saatler'),
                value: settings.quietHoursEnabled,
                onChanged: (v) => ref
                    .read(notificationSettingsProvider.notifier)
                    .toggle('quiet_hours_enabled', v),
              ),
              const Divider(),
              ListTile(
                title: const Text('FCM Token'),
                subtitle: Text(
                  settings.hasFcmToken
                      ? 'Kayıtlı (push sonraki sprint)'
                      : 'Henüz yok — stub senkronize edilebilir',
                ),
                trailing: TextButton(
                  onPressed: () async {
                    final token = await ref
                        .read(appNotificationServiceProvider)
                        .getFcmToken();
                    if (token != null) {
                      await ref
                          .read(notificationSettingsProvider.notifier)
                          .syncFcmTokenStub(token);
                    }
                  },
                  child: const Text('Senkronize'),
                ),
              ),
              const Divider(),
              const ListTile(
                title: Text('Öğrenme araçları'),
                dense: true,
              ),
              ListTile(
                leading: const Icon(Icons.chat_outlined),
                title: const Text('AI Sohbet'),
                subtitle: const Text('Koç ile konuş, soru sor'),
                onTap: () => context.push('/ai-chat'),
              ),
              ListTile(
                leading: const Icon(Icons.auto_awesome),
                title: const Text('Önerilen çalışma planı'),
                subtitle: const Text('Adaptive planner'),
                onTap: () => context.push('/planner'),
              ),
              ListTile(
                leading: const Icon(Icons.science_outlined),
                title: const Text('Assessment'),
                subtitle: const Text('Kalibrasyon ve challenge'),
                onTap: () => context.push('/assessment'),
              ),
              ListTile(
                leading: const Icon(Icons.flag_outlined),
                title: const Text('Hedefler'),
                onTap: () => context.push('/goals'),
              ),
              ListTile(
                leading: const Icon(Icons.emoji_events_outlined),
                title: const Text('Başarımlar'),
                onTap: () => context.push('/achievements'),
              ),
              ListTile(
                leading: const Icon(Icons.psychology_outlined),
                title: const Text('AI bellek'),
                onTap: () => context.push('/memory'),
              ),
              ListTile(
                leading: const Icon(Icons.tune_outlined),
                title: const Text('AI ayarları'),
                onTap: () => context.push('/ai-settings'),
              ),
              ListTile(
                leading: const Icon(Icons.timer_outlined),
                title: const Text('Pomodoro'),
                subtitle: const Text('Odak oturumu başlat'),
                onTap: () => context.push('/pomodoro'),
              ),
              ListTile(
                leading: const Icon(Icons.assignment_outlined),
                title: const Text('Denemeler'),
                subtitle: const Text('Sonuç ekle / geçmiş'),
                onTap: () => context.push('/exams'),
              ),
              ListTile(
                leading: const Icon(Icons.quiz_outlined),
                title: const Text('Soru Kaydı'),
                onTap: () => context.push('/questions'),
              ),
              ListTile(
                leading: const Icon(Icons.feedback_outlined),
                title: const Text('Geri bildirim'),
                onTap: () => context.push('/feedback'),
              ),
              ListTile(
                leading: const Icon(Icons.insights_outlined),
                title: const Text('Analytics'),
                subtitle: const Text('RC2 metrik paneli'),
                onTap: () => context.push('/analytics'),
              ),
              const Divider(),
              ListTile(
                title: const Text(
                  'Çıkış Yap',
                  style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                ),
                leading: const Icon(Icons.logout_rounded, color: Colors.red),
                onTap: () async {
                  await ref.read(authProvider.notifier).logout();
                },
              ),
              const SizedBox(height: 24),
            ],
          ),
      },
    );
  }
}
