import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/study_plan_provider.dart';
import '../widgets/study_plan_form.dart';

/// Add Study Plan Screen — seçili güne yeni bir çalışma planı kalemi ekler.
class AddStudyPlanScreen extends ConsumerWidget {
  const AddStudyPlanScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Plan Ekle')),
      body: StudyPlanForm(
        submitLabel: 'Planı Kaydet',
        onSubmit: (result) async {
          await ref.read(studyPlanProvider.notifier).createPlan(
                title: result.title,
                subject: result.subject,
                topic: result.topic,
                targetQuestionCount: result.targetQuestionCount,
                estimatedMinutes: result.estimatedMinutes,
                plannedStartTime: result.plannedStartTime,
                plannedEndTime: result.plannedEndTime,
              );
          if (context.mounted) Navigator.of(context).pop();
        },
      ),
    );
  }
}
