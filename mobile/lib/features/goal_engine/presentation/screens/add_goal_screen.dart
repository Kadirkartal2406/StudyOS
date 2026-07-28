import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../providers/goal_provider.dart';
import '../widgets/goal_form.dart';

class AddGoalScreen extends ConsumerWidget {
  const AddGoalScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(learningProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Hedef Ekle')),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => GoalForm(
          submitLabel: 'Kaydet',
          onSubmit: (result) => _save(context, ref, result),
        ),
        data: (profile) => GoalForm(
          submitLabel: 'Kaydet',
          allowedExamTypes: profile.allowedExamTypes,
          defaultExamType: profile.activeExamType ?? profile.primaryExamType,
          subjectOptions: profile.subjectNames,
          onSubmit: (result) => _save(context, ref, result),
        ),
      ),
    );
  }

  Future<void> _save(
    BuildContext context,
    WidgetRef ref,
    GoalFormResult result,
  ) async {
    await ref.read(goalProvider.notifier).create(result.toCreateBody());
    ref.invalidate(dashboardProvider);
    if (context.mounted) Navigator.of(context).pop();
  }
}
