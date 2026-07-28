/// Sprint 9 — Living Plan öneri banner'ı.
/// Sistem tarafından oluşturulan plan önerileri varsa gösterilir.
library;

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';

// ── Provider ─────────────────────────────────────────────────────────────────

class _Suggestion {
  const _Suggestion({required this.id, required this.targetExam, this.overview});
  final String id;
  final String targetExam;
  final String? overview;
}

final _suggestionsProvider = FutureProvider<List<_Suggestion>>((ref) async {
  final dio = ref.watch(dioClientProvider);
  try {
    final resp = await dio.get<Map<String, dynamic>>('/planner/suggestions');
    final data = resp.data?['data'];
    if (data is! List) return [];
    return (data)
        .map((e) {
          final m = e as Map<String, dynamic>;
          final rationale = m['rationale'] as Map<String, dynamic>?;
          return _Suggestion(
            id: m['id']?.toString() ?? '',
            targetExam: m['target_exam']?.toString() ?? '',
            overview: rationale?['overview']?.toString(),
          );
        })
        .where((s) => s.id.isNotEmpty)
        .toList();
  } catch (_) {
    return [];
  }
});

// ── Widget ────────────────────────────────────────────────────────────────────

class SuggestionBanner extends ConsumerWidget {
  const SuggestionBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(_suggestionsProvider);
    return state.when(
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
      data: (suggestions) {
        if (suggestions.isEmpty) return const SizedBox.shrink();
        final first = suggestions.first;
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          color: Theme.of(context).colorScheme.secondaryContainer,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.auto_awesome_rounded,
                      size: 18,
                      color: Theme.of(context).colorScheme.onSecondaryContainer,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Sistem bir plan önerisi hazırladı',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Theme.of(context).colorScheme.onSecondaryContainer,
                          ),
                    ),
                  ],
                ),
                if (first.overview != null && first.overview!.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(
                    first.overview!,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context)
                              .colorScheme
                              .onSecondaryContainer
                              .withOpacity(0.8),
                        ),
                  ),
                ],
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () =>
                          _respondToSuggestion(context, ref, first.id, accept: false),
                      child: const Text('Reddet'),
                    ),
                    const SizedBox(width: 8),
                    FilledButton.tonal(
                      onPressed: () =>
                          _respondToSuggestion(context, ref, first.id, accept: true),
                      child: const Text('Kabul Et'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _respondToSuggestion(
    BuildContext context,
    WidgetRef ref,
    String id, {
    required bool accept,
  }) async {
    final dio = ref.read(dioClientProvider);
    final action = accept ? 'accept' : 'reject';
    try {
      if (accept) {
        await dio.post<dynamic>('/planner/$id/accept', data: {'weeks': 4});
      } else {
        await dio.post<dynamic>('/planner/suggestions/$id/reject');
      }
      ref.invalidate(_suggestionsProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(accept ? 'Plan kabul edildi!' : 'Öneri reddedildi.'),
          ),
        );
      }
    } on DioException {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Bir hata oluştu, lütfen tekrar dene.')),
        );
      }
    }
  }
}
