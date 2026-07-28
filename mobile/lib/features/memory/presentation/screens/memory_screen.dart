import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../domain/entities/memory_entity.dart';
import '../providers/memory_provider.dart';
import '../providers/memory_state.dart';

/// AI Memory listesi + gizlilik — Sprint-2.3
class MemoryScreen extends ConsumerStatefulWidget {
  const MemoryScreen({super.key});

  @override
  ConsumerState<MemoryScreen> createState() => _MemoryScreenState();
}

class _MemoryScreenState extends ConsumerState<MemoryScreen> {
  final _searchCtrl = TextEditingController();

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(memoryProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Bellek'),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => ref.read(memoryProvider.notifier).load(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/memory/add'),
        icon: const Icon(Icons.add),
        label: const Text('Ekle'),
      ),
      body: switch (state) {
        MemoryInitial() || MemoryLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        MemoryError(:final message) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(message, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () => ref.read(memoryProvider.notifier).load(),
                    child: const Text('Tekrar Dene'),
                  ),
                ],
              ),
            ),
          ),
        MemoryLoaded(
          :final items,
          :final aiMemoryEnabled,
          :final errorMessage,
          :final infoMessage,
        ) =>
          RefreshIndicator(
            onRefresh: () => ref.read(memoryProvider.notifier).load(),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 96),
              children: [
                if (errorMessage != null)
                  _Banner(text: errorMessage, isError: true),
                if (infoMessage != null)
                  _Banner(text: infoMessage, isError: false),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('AI bellek etkin'),
                  subtitle: const Text(
                    'Kapalıyken sohbetten yeni bellek yazılmaz',
                  ),
                  value: aiMemoryEnabled,
                  onChanged: (v) =>
                      ref.read(memoryProvider.notifier).setEnabled(v),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          final text = await ref
                              .read(memoryProvider.notifier)
                              .exportSummary();
                          if (text == null || !context.mounted) return;
                          await Clipboard.setData(ClipboardData(text: text));
                          if (!context.mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Bellekler panoya kopyalandı'),
                            ),
                          );
                        },
                        icon: const Icon(Icons.upload_outlined),
                        label: const Text('Dışa aktar'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          final ok = await showDialog<bool>(
                            context: context,
                            builder: (ctx) => AlertDialog(
                              title: const Text('Tüm bellekleri sil?'),
                              content: const Text(
                                'Bu işlem geri alınamaz.',
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(ctx, false),
                                  child: const Text('Vazgeç'),
                                ),
                                FilledButton(
                                  onPressed: () => Navigator.pop(ctx, true),
                                  child: const Text('Sil'),
                                ),
                              ],
                            ),
                          );
                          if (ok == true) {
                            await ref.read(memoryProvider.notifier).clearAll();
                          }
                        },
                        icon: const Icon(Icons.delete_sweep_outlined),
                        label: const Text('Temizle'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _searchCtrl,
                  decoration: const InputDecoration(
                    hintText: 'Bellek ara…',
                    prefixIcon: Icon(Icons.search),
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (v) =>
                      ref.read(memoryProvider.notifier).search(v),
                ),
                const SizedBox(height: 16),
                if (items.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 48),
                    child: Center(
                      child: Text(
                        'Henüz bellek yok. Manuel ekleyin veya sohbet edin.',
                      ),
                    ),
                  )
                else
                  ...items.map(
                    (m) => _MemoryTile(
                      memory: m,
                      onTap: () => context.push('/memory/${m.id}'),
                      onDelete: () =>
                          ref.read(memoryProvider.notifier).delete(m.id),
                    ),
                  ),
              ],
            ),
          ),
      },
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({required this.text, required this.isError});

  final String text;
  final bool isError;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isError
            ? scheme.errorContainer
            : scheme.secondaryContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(text),
    );
  }
}

class _MemoryTile extends StatelessWidget {
  const _MemoryTile({
    required this.memory,
    required this.onTap,
    required this.onDelete,
  });

  final MemoryEntity memory;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        onTap: onTap,
        title: Text(memory.content, maxLines: 2, overflow: TextOverflow.ellipsis),
        subtitle: Text(
          '${memory.category.label} · önem ${(memory.importance * 100).round()}%',
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline),
          onPressed: onDelete,
        ),
      ),
    );
  }
}
