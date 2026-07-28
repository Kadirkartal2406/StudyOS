import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../domain/entities/question_enums.dart';
import '../providers/question_tracking_provider.dart';
import '../widgets/question_form.dart';

class AddQuestionScreen extends ConsumerWidget {
  const AddQuestionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(learningProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Soru Kaydı Ekle')),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => QuestionForm(
          submitLabel: 'Kaydet',
          onSubmit: (result) => _save(context, ref, result),
        ),
        data: (profile) {
          final subjectOpts = profile.activeSubjects
              .map((s) => SubjectOption(name: s.subjectName, code: s.subjectCode))
              .toList();
          return QuestionForm(
            submitLabel: 'Kaydet',
            allowedExamTypes: profile.allowedExamTypeEnums.isEmpty
                ? null
                : profile.allowedExamTypeEnums,
            defaultExamType: ExamType.fromApi(
                  profile.activeExamType ?? profile.resolvedPrimaryExamType,
                ),
            subjectOptions: subjectOpts,
            onSubmit: (result) => _save(context, ref, result),
          );
        },
      ),
    );
  }

  Future<void> _save(
    BuildContext context,
    WidgetRef ref,
    QuestionFormResult result,
  ) async {
    await ref.read(questionMutationProvider).create(result.toApiBody());
    ref.invalidate(questionListProvider);
    ref.invalidate(questionStatsProvider);
    ref.invalidate(dashboardProvider);
    invalidateLearningProfile(ref);
    if (context.mounted) Navigator.of(context).pop();
  }
}
