import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';
import '../../domain/entities/ai_chat_entities.dart';
import '../providers/ai_chat_provider.dart';
import '../providers/ai_chat_state.dart';
import '../widgets/message_bubble.dart';

/// Chat ekranı — Sprint-2.2 (streaming-ready tek shot)
class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key, this.conversationId});

  final String? conversationId;

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _controller = TextEditingController();
  final _scroll = ScrollController();

  @override
  void initState() {
    super.initState();
    final id = widget.conversationId;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (id == null || id == 'new') {
        ref.read(aiChatProvider.notifier).startNewChat();
      } else {
        ref.read(aiChatProvider.notifier).openConversation(id);
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scroll.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final text = _controller.text;
    _controller.clear();
    await ref.read(aiChatProvider.notifier).sendMessage(text);
    if (_scroll.hasClients) {
      await _scroll.animateTo(
        _scroll.position.maxScrollExtent + 80,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(aiChatProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Çalışma Koçu'),
        actions: [
          IconButton(
            tooltip: 'AI Ayarları',
            onPressed: () => context.push('/ai-settings'),
            icon: const Icon(Icons.tune_rounded),
          ),
          IconButton(
            tooltip: 'Yeniden üret',
            onPressed: () => ref.read(aiChatProvider.notifier).regenerate(),
            icon: const Icon(Icons.refresh_rounded),
          ),
          IconButton(
            tooltip: 'Tekrar dene',
            onPressed: () => ref.read(aiChatProvider.notifier).retryLast(),
            icon: const Icon(Icons.replay_rounded),
          ),
          TextButton(
            onPressed: () => context.push('/ai-coach'),
            child: const Text('İçgörüler'),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: switch (state) {
              AiChatInitial() || AiChatLoading() => const Center(
                  child: CircularProgressIndicator(),
                ),
              AiChatError(:final message) => Center(child: Text(message)),
              AiChatLoaded(
                :final messages,
                :final isTyping,
                :final errorMessage,
              ) =>
                ListView(
                  controller: _scroll,
                  padding: const EdgeInsets.all(16),
                  children: [
                    if (messages.isEmpty)
                      const Padding(
                        padding: EdgeInsets.only(bottom: 16),
                        child: Text(
                          'Merhaba! Çalışma hedeflerin ve istatistiklerin '
                          'bağlamında soru sorabilirsin.',
                        ),
                      ),
                    for (final m in messages) ...[
                      MessageBubble(message: m),
                      if (m.role == ChatMessageRole.assistant)
                        _PlanProposalCard(message: m),
                    ],
                    if (isTyping) const TypingIndicator(),
                    if (errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(
                          errorMessage,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                  ],
                ),
            },
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      minLines: 1,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        hintText: 'Mesaj yaz…',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => _send(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  if (state is AiChatLoaded && state.sending)
                    IconButton.filled(
                      tooltip: 'İptal',
                      onPressed: () =>
                          ref.read(aiChatProvider.notifier).cancelSend(),
                      icon: const Icon(Icons.stop_rounded),
                    )
                  else
                    IconButton.filled(
                      onPressed: _send,
                      icon: const Icon(Icons.send_rounded),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PlanProposalCard extends ConsumerStatefulWidget {
  const _PlanProposalCard({required this.message});

  final ChatMessageEntity message;

  @override
  ConsumerState<_PlanProposalCard> createState() => _PlanProposalCardState();
}

class _PlanProposalCardState extends ConsumerState<_PlanProposalCard> {
  bool _resolved = false;
  bool _busy = false;

  @override
  Widget build(BuildContext context) {
    if (_resolved) return const SizedBox.shrink();
    final raw = widget.message.metadata['plan_proposal'];
    if (raw is! Map) return const SizedBox.shrink();
    final draftId = raw['draft_id']?.toString();
    if (draftId == null || draftId.isEmpty) return const SizedBox.shrink();
    final reason = raw['reason']?.toString() ?? '';
    final summary = raw['summary']?.toString();
    final status = raw['status']?.toString() ?? 'pending';
    if (status != 'pending') return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.only(bottom: 12, left: 8, right: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Plan önerisi (onay gerekli)',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            if (summary != null && summary.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(summary),
            ],
            if (reason.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                reason,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
            const SizedBox(height: 10),
            Row(
              children: [
                FilledButton(
                  onPressed: _busy
                      ? null
                      : () => _decide(draftId, accept: true),
                  child: const Text('Uygula'),
                ),
                const SizedBox(width: 8),
                OutlinedButton(
                  onPressed: _busy
                      ? null
                      : () => _decide(draftId, accept: false),
                  child: const Text('Reddet'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _decide(String draftId, {required bool accept}) async {
    setState(() => _busy = true);
    final dio = ref.read(dioClientProvider);
    try {
      if (accept) {
        await dio.post<dynamic>(ApiEndpoints.plannerSuggestionAccept(draftId));
      } else {
        await dio.post<dynamic>(ApiEndpoints.plannerSuggestionReject(draftId));
      }
      if (!mounted) return;
      setState(() {
        _resolved = true;
        _busy = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(accept ? 'Plan uygulandı' : 'Plan önerisi reddedildi'),
        ),
      );
      if (accept) {
        context.push('/study-plan');
      }
    } on DioException catch (e) {
      if (!mounted) return;
      setState(() => _busy = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message ?? 'İşlem başarısız')),
      );
    }
  }
}
