import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/platform/platform_providers.dart';

/// Dashboard — bildirim izni + widget durumu (Sprint-1.8).
class OsIntegrationCard extends ConsumerStatefulWidget {
  const OsIntegrationCard({super.key});

  @override
  ConsumerState<OsIntegrationCard> createState() => _OsIntegrationCardState();
}

class _OsIntegrationCardState extends ConsumerState<OsIntegrationCard> {
  bool? _allowed;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final allowed =
        await ref.read(platformServiceProvider).areNotificationsAllowed();
    if (mounted) setState(() => _allowed = allowed);
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Sistem Entegrasyonu',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 12),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(
                _allowed == true
                    ? Icons.notifications_active_outlined
                    : Icons.notifications_off_outlined,
                color: _allowed == true ? colorScheme.primary : colorScheme.error,
              ),
              title: Text(
                _allowed == true
                    ? 'Bildirim izni açık'
                    : 'Bildirim izni gerekli',
              ),
              trailing: _allowed == true
                  ? null
                  : TextButton(
                      onPressed: () async {
                        final platform = ref.read(platformServiceProvider);
                        final ok =
                            await platform.requestNotificationPermission();
                        if (!ok) {
                          await platform.openSystemNotificationSettings();
                        }
                        await _refresh();
                      },
                      child: const Text('İzin Ver'),
                    ),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: Icon(Icons.widgets_outlined, color: colorScheme.tertiary),
              title: const Text('Ana ekran widget'),
              subtitle: const Text(
                'Medium widget — ana ekrana ekleyebilirsin (Android)',
              ),
            ),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => context.push('/notification-settings'),
                child: const Text('Bildirim Ayarları'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
