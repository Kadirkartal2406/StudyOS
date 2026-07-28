/// Sprint 13 — In-app notification bell widget.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/network/dio_client.dart';

// ── Model ─────────────────────────────────────────────────────────────────────

class _InAppNotification {
  const _InAppNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    this.deepLink,
  });
  final String id;
  final String type;
  final String title;
  final String body;
  final String? deepLink;
}

// ── Provider ──────────────────────────────────────────────────────────────────

final notificationsProvider = FutureProvider<List<_InAppNotification>>((ref) async {
  final dio = ref.watch(dioClientProvider);
  try {
    final resp = await dio.get<Map<String, dynamic>>('/notifications');
    final data = (resp.data?['data'] as Map<String, dynamic>?)?['notifications'];
    if (data is! List) return [];
    return (data)
        .map((e) {
          final m = e as Map<String, dynamic>;
          return _InAppNotification(
            id: m['id']?.toString() ?? '',
            type: m['type']?.toString() ?? '',
            title: m['title']?.toString() ?? '',
            body: m['body']?.toString() ?? '',
            deepLink: m['deep_link']?.toString(),
          );
        })
        .where((n) => n.id.isNotEmpty)
        .toList();
  } catch (_) {
    return [];
  }
});

// ── Widget ────────────────────────────────────────────────────────────────────

class NotificationBell extends ConsumerWidget {
  const NotificationBell({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(notificationsProvider);
    final count = state.valueOrNull?.length ?? 0;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        IconButton(
          tooltip: 'Bildirimler',
          icon: const Icon(Icons.notifications_outlined),
          onPressed: () => _showPanel(context, ref),
        ),
        if (count > 0)
          Positioned(
            top: 6,
            right: 6,
            child: Container(
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.error,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  '$count',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onError,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }

  void _showPanel(BuildContext context, WidgetRef ref) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _NotificationPanel(ref: ref),
    );
  }
}

class _NotificationPanel extends StatelessWidget {
  const _NotificationPanel({required this.ref});
  final WidgetRef ref;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(notificationsProvider);

    return DraggableScrollableSheet(
      initialChildSize: 0.5,
      minChildSize: 0.3,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, controller) => Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Text(
                  'Bildirimler',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.refresh_rounded),
                  onPressed: () => ref.invalidate(notificationsProvider),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: state.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, __) => const Center(child: Text('Bildirimler yüklenemedi')),
              data: (notes) {
                if (notes.isEmpty) {
                  return const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.notifications_none_rounded, size: 48),
                        SizedBox(height: 8),
                        Text('Yeni bildirim yok'),
                      ],
                    ),
                  );
                }
                return ListView.separated(
                  controller: controller,
                  itemCount: notes.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, i) {
                    final n = notes[i];
                    return ListTile(
                      leading: _iconFor(n.type),
                      title: Text(n.title),
                      subtitle: Text(n.body),
                      onTap: n.deepLink != null
                          ? () {
                              Navigator.of(context).pop();
                              context.push(n.deepLink!);
                            }
                          : null,
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _iconFor(String type) {
    final (icon, color) = switch (type) {
      'revision_due' => (Icons.replay_rounded, Colors.orange),
      'plan_suggestion' => (Icons.auto_awesome_rounded, Colors.purple),
      'streak_risk' => (Icons.local_fire_department_rounded, Colors.red),
      'milestone' => (Icons.emoji_events_rounded, Colors.amber),
      _ => (Icons.info_outline_rounded, Colors.blue),
    };
    return CircleAvatar(
      radius: 20,
      backgroundColor: color.withOpacity(0.12),
      child: Icon(icon, color: color, size: 18),
    );
  }
}
