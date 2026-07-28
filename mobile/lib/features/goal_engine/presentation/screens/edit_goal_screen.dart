import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../providers/goal_provider.dart';
import '../widgets/goal_form.dart';

class EditGoalScreen extends ConsumerWidget {
  const EditGoalScreen({super.key, required this.goalId});

  final String goalId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(goalDetailProvider(goalId));
    final profile = ref.watch(learningProfileProvider).valueOrNull;

    return Scaffold(
      appBar: AppBar(title: const Text('Hedefi Düzenle')),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (goal) => GoalForm(
          submitLabel: 'Güncelle',
          allowStatusEdit: true,
          allowedExamTypes: profile?.allowedExamTypes,
          defaultExamType: goal.examType ??
              profile?.activeExamType ??
              profile?.primaryExamType,
          subjectOptions: profile?.subjectNames ?? const [],
          initial: GoalFormResult(
            title: goal.title,
            description: goal.description,
            productGoalType: goal.productGoalType,
            goalType: goal.goalType,
            targetValue: goal.targetValue,
            priority: goal.priority,
            period: goal.period,
            subject: goal.subject,
            topic: goal.topic,
            examType: goal.examType,
            startDate: goal.startDate,
            endDate: goal.endDate,
            status: goal.status,
          ),
          onSubmit: (result) async {
            await ref
                .read(goalProvider.notifier)
                .update(goalId, result.toUpdateBody());
            ref.invalidate(goalDetailProvider(goalId));
            ref.invalidate(dashboardProvider);
            if (context.mounted) Navigator.of(context).pop();
          },
        ),
      ),
    );
  }
}
