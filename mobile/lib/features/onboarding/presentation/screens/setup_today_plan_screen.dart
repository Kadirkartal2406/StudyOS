import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../adaptive_planner/domain/entities/planner_entity.dart';
import '../../../adaptive_planner/presentation/providers/planner_provider.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../providers/first_run_phase_provider.dart';

/// Onay sonrası: bugün çalışılacak dersler.
class SetupTodayPlanScreen extends ConsumerWidget {
  const SetupTodayPlanScreen({super.key});

  List<PlannerItemEntity> _todayItems(PlannerDraftEntity draft) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    return draft.items.where((item) {
      final d = DateTime(
        item.studyDate.year,
        item.studyDate.month,
        item.studyDate.day,
      );
      return d == today;
    }).toList();
  }

  PlannerDraftEntity? _draftFrom(PlannerUiState state) {
    return switch (state) {
      PlannerAccepted(:final draft) => draft,
      PlannerPreview(:final draft) => draft,
      _ => null,
    };
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final draft = _draftFrom(ref.watch(plannerProvider));
    final items = draft == null ? <PlannerItemEntity>[] : _todayItems(draft);
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                name.isEmpty ? 'Bugün ne çalışacaksın?' : '$name, bugün bunlar',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Planın onaylandı. Bugünkü derslerin aşağıda.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
              ),
              const SizedBox(height: 20),
              Expanded(
                child: items.isEmpty
                    ? Center(
                        child: Text(
                          'Bugün için planlı blok yok.\n'
                          'Yarın veya bir sonraki çalışma gününde devam.',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      )
                    : ListView.separated(
                        itemCount: items.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, i) {
                          final item = items[i];
                          return Card(
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: scheme.primaryContainer,
                                child: Text(
                                  '${i + 1}',
                                  style: TextStyle(
                                    color: scheme.onPrimaryContainer,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                              title: Text(
                                item.subject,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              subtitle: Text(
                                [
                                  if (item.startTime != null &&
                                      item.endTime != null)
                                    '${item.startTime}–${item.endTime}',
                                  if (item.topic != null &&
                                      item.topic!.isNotEmpty)
                                    item.topic!,
                                  if (item.title.isNotEmpty) item.title,
                                  '${item.estimatedMinutes} dk',
                                  if (item.targetQuestionCount > 0)
                                    '${item.targetQuestionCount} soru',
                                ].join(' · '),
                              ),
                              isThreeLine: true,
                            ),
                          );
                        },
                      ),
              ),
              FilledButton(
                onPressed: () async {
                  await ref
                      .read(firstRunPhaseProvider.notifier)
                      .setPhase('tour');
                  if (!context.mounted) return;
                  context.go('/setup/tour');
                },
                child: const Text('Tanıtıma geç'),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => context.push('/planner'),
                child: const Text('Tüm planı gör'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
