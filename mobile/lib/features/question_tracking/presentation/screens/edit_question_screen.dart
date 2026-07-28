import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../providers/question_tracking_provider.dart';
import '../widgets/question_form.dart';

class EditQuestionScreen extends ConsumerWidget {
  const EditQuestionScreen({super.key, required this.recordId});

  final String recordId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(questionDetailProvider(recordId));
    final profileAsync = ref.watch(learningProfileProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Soru Kaydını Düzenle')),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('$e')),
        data: (entity) {
          final profile = profileAsync.valueOrNull;
          final subjectOpts = profile?.activeSubjects
                  .map((s) =>
                      SubjectOption(name: s.subjectName, code: s.subjectCode))
                  .toList() ??
              const [];
          return QuestionForm(
            submitLabel: 'Güncelle',
            allowedExamTypes: profile?.allowedExamTypeEnums,
            defaultExamType:
                entity.examType ?? profile?.primaryExamTypeEnum,
            subjectOptions: subjectOpts,
            initial: QuestionFormResult(
              subject: entity.subject,
              topic: entity.topic,
              questionCount: entity.questionCount,
              correctCount: entity.correctCount,
              wrongCount: entity.wrongCount,
              blankCount: entity.blankCount,
              durationMinutes: entity.durationMinutes,
              difficulty: entity.difficulty,
              source: entity.source,
              examType: entity.examType,
              note: entity.note,
            ),
            onSubmit: (result) async {
              await ref
                  .read(questionMutationProvider)
                  .update(recordId, result.toApiBody());
              ref.invalidate(questionListProvider);
              ref.invalidate(questionDetailProvider(recordId));
              ref.invalidate(questionStatsProvider);
              ref.invalidate(dashboardProvider);
              invalidateLearningProfile(ref);
              if (context.mounted) Navigator.of(context).pop();
            },
          );
        },
      ),
    );
  }
}
