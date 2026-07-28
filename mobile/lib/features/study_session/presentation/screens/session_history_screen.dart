import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../domain/entities/study_session_entity.dart';
import '../../domain/entities/study_session_status.dart';
import '../providers/session_history_provider.dart';
import '../providers/session_history_state.dart';

class SessionHistoryScreen extends ConsumerStatefulWidget {
  const SessionHistoryScreen({super.key});

  @override
  ConsumerState<SessionHistoryScreen> createState() =>
      _SessionHistoryScreenState();
}

class _SessionHistoryScreenState extends ConsumerState<SessionHistoryScreen> {
  final _searchController = TextEditingController();
  String? _statusFilter;
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(() {
      if (_scrollController.position.pixels >
          _scrollController.position.maxScrollExtent - 200) {
        ref.read(sessionHistoryProvider.notifier).loadMore();
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _apply() {
    ref.read(sessionHistoryProvider.notifier).applyFilters(
          statusFilter: _statusFilter,
          searchQuery: _searchController.text.trim().isEmpty
              ? null
              : _searchController.text.trim(),
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(sessionHistoryProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Oturum Geçmişi')),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 0),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Column(
              children: [
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Plan adı ara',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.filter_list),
                      onPressed: _apply,
                    ),
                    border: const OutlineInputBorder(),
                    isDense: true,
                  ),
                  onSubmitted: (_) => _apply(),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: [
                    ChoiceChip(
                      label: const Text('Tümü'),
                      selected: _statusFilter == null,
                      onSelected: (_) {
                        setState(() => _statusFilter = null);
                        _apply();
                      },
                    ),
                    ChoiceChip(
                      label: const Text('Tamamlanan'),
                      selected: _statusFilter == 'completed',
                      onSelected: (_) {
                        setState(() => _statusFilter = 'completed');
                        _apply();
                      },
                    ),
                    ChoiceChip(
                      label: const Text('Devam eden'),
                      selected: _statusFilter == 'running',
                      onSelected: (_) {
                        setState(() => _statusFilter = 'running');
                        _apply();
                      },
                    ),
                    ChoiceChip(
                      label: const Text('Duraklatılan'),
                      selected: _statusFilter == 'paused',
                      onSelected: (_) {
                        setState(() => _statusFilter = 'paused');
                        _apply();
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: switch (state) {
              SessionHistoryInitial() || SessionHistoryLoading() =>
                const Center(child: CircularProgressIndicator()),
              SessionHistoryError(:final message) => Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(message),
                      const SizedBox(height: 12),
                      FilledButton(
                        onPressed: () =>
                            ref.read(sessionHistoryProvider.notifier).load(),
                        child: const Text('Tekrar Dene'),
                      ),
                    ],
                  ),
                ),
              SessionHistoryLoaded(:final items, :final isLoadingMore) =>
                items.isEmpty
                    ? const Center(child: Text('Kayıt bulunamadı'))
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.all(16),
                        itemCount: items.length + (isLoadingMore ? 1 : 0),
                        itemBuilder: (context, index) {
                          if (index >= items.length) {
                            return const Padding(
                              padding: EdgeInsets.all(16),
                              child: Center(child: CircularProgressIndicator()),
                            );
                          }
                          return _SessionCard(session: items[index]);
                        },
                      ),
            },
          ),
        ],
      ),
    );
  }
}

class _SessionCard extends StatelessWidget {
  const _SessionCard({required this.session});

  final StudySessionEntity session;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd MMM HH:mm', 'tr_TR');
    final end = session.endedAt != null ? fmt.format(session.endedAt!.toLocal()) : '—';
    final statusLabel = switch (session.status) {
      StudySessionStatus.completed => 'Tamamlandı',
      StudySessionStatus.running => 'Devam ediyor',
      StudySessionStatus.paused => 'Duraklatıldı',
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: () => context.push('/session-history/${session.id}'),
        title: Text(session.planTitle ?? 'Serbest çalışma'),
        subtitle: Text(
          '${fmt.format(session.startedAt.toLocal())} → $end\n'
          '${session.actualDurationMinutes} dk · ${session.completedQuestions} soru · $statusLabel',
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
