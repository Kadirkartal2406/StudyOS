import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/ai_chat_provider.dart';
import '../providers/ai_chat_state.dart';

/// Sohbet listesi — Sprint-2.2
class ConversationsScreen extends ConsumerWidget {
  const ConversationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(aiChatProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Sohbet'),
        actions: [
          TextButton(
            onPressed: () => context.push('/ai-settings'),
            child: const Text('AI'),
          ),
          TextButton(
            onPressed: () => context.push('/memory'),
            child: const Text('Bellek'),
          ),
          TextButton(
            onPressed: () => context.push('/ai-coach'),
            child: const Text('İçgörüler'),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ref.read(aiChatProvider.notifier).startNewChat();
          context.push('/ai-chat/new');
        },
        icon: const Icon(Icons.chat_bubble_outline_rounded),
        label: const Text('Yeni sohbet'),
      ),
      body: switch (state) {
        AiChatInitial() || AiChatLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        AiChatError(:final message) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(message, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () =>
                        ref.read(aiChatProvider.notifier).loadConversations(),
                    child: const Text('Tekrar Dene'),
                  ),
                ],
              ),
            ),
          ),
        AiChatLoaded(:final conversations) => conversations.isEmpty
            ? const Center(child: Text('Henüz sohbet yok. Yeni sohbet başlat.'))
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: conversations.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final c = conversations[index];
                  return ListTile(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(
                        color: Theme.of(context).colorScheme.outlineVariant,
                      ),
                    ),
                    title: Text(c.title),
                    subtitle: Text('${c.messageCount} mesaj'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline),
                      onPressed: () => ref
                          .read(aiChatProvider.notifier)
                          .deleteConversation(c.id),
                    ),
                    onTap: () => context.push('/ai-chat/${c.id}'),
                  );
                },
              ),
      },
    );
  }
}
