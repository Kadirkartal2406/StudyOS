import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/study_plan_entity.dart';
import '../providers/study_plan_provider.dart';
import '../providers/study_plan_state.dart';
import '../widgets/study_plan_form.dart';

StudyPlanEntity? _findPlanById(List<StudyPlanEntity> plans, String id) {
  for (final plan in plans) {
    if (plan.id == id) return plan;
  }
  return null;
}

/// Edit Study Plan Screen — mevcut bir çalışma planı kalemini düzenler.
class EditStudyPlanScreen extends ConsumerStatefulWidget {
  const EditStudyPlanScreen({super.key, required this.planId});

  final String planId;

  @override
  ConsumerState<EditStudyPlanScreen> createState() =>
      _EditStudyPlanScreenState();
}

class _EditStudyPlanScreenState extends ConsumerState<EditStudyPlanScreen> {
  StudyPlanEntity? _plan;
  Object? _error;
  bool _loading = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final state = ref.read(studyPlanProvider);
      StudyPlanEntity? cached;
      if (state is StudyPlanLoaded) {
        cached = _findPlanById(state.plans, widget.planId);
      }
      if (cached != null) {
        setState(() {
          _plan = cached;
          _loading = false;
        });
        return;
      }
      final fetched =
          await ref.read(studyPlanProvider.notifier).fetchPlanById(widget.planId);
      if (!mounted) return;
      setState(() {
        _plan = fetched;
        _loading = false;
        if (fetched == null) {
          _error = 'Plan bulunamadı';
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Planı Düzenle')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    final plan = _plan;
    if (plan == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Planı Düzenle')),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error?.toString() ?? 'Plan bulunamadı'),
              const SizedBox(height: 12),
              FilledButton(onPressed: _load, child: const Text('Tekrar dene')),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Planı Düzenle')),
      body: StudyPlanForm(
        submitLabel: _saving ? 'Kaydediliyor…' : 'Değişiklikleri Kaydet',
        initialTitle: plan.title,
        initialSubject: plan.subject,
        initialTopic: plan.topic,
        initialTargetQuestionCount: plan.targetQuestionCount,
        initialEstimatedMinutes: plan.estimatedMinutes,
        initialStartTime: plan.plannedStartTime,
        initialEndTime: plan.plannedEndTime,
        onSubmit: (result) async {
          if (_saving) return;
          setState(() => _saving = true);
          try {
            await ref.read(studyPlanProvider.notifier).updatePlan(
                  id: plan.id,
                  title: result.title,
                  subject: result.subject,
                  topic: result.topic,
                  targetQuestionCount: result.targetQuestionCount,
                  estimatedMinutes: result.estimatedMinutes,
                  plannedStartTime: result.plannedStartTime,
                  plannedEndTime: result.plannedEndTime,
                  studyDate: plan.studyDate,
                );
            if (context.mounted) Navigator.of(context).pop();
          } finally {
            if (mounted) setState(() => _saving = false);
          }
        },
      ),
    );
  }
}
