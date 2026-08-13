import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/widgets/app_error_view.dart';
import '../../../../shared/widgets/study_icons.dart';
import '../../../exam_catalog/presentation/providers/exam_catalog_provider.dart';
import '../../../onboarding/domain/entities/learning_profile_entity.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../question_tracking/presentation/providers/topic_picker_provider.dart';
import '../../data/topic_quiz_remote_datasource.dart';

/// Standalone AI question generation — separate from Topic Test Catalog.
class SoruUretScreen extends ConsumerStatefulWidget {
  const SoruUretScreen({super.key});

  @override
  ConsumerState<SoruUretScreen> createState() => _SoruUretScreenState();
}

class _SoruUretScreenState extends ConsumerState<SoruUretScreen> {
  /// Backend `QuizGenerateRequest.count` is ge=1, le=15.
  static const _counts = [5, 10, 15];

  String? _exam;
  String? _subjectCode;
  String? _topicCode;
  int _count = 5;
  String _difficulty = 'medium';
  bool _generating = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrapFromProfile());
  }

  void _bootstrapFromProfile() {
    final profile = ref.read(learningProfileProvider).valueOrNull;
    if (profile == null) return;
    final exam = (profile.activeExamType ?? profile.primaryExamType ?? '')
        .trim()
        .toLowerCase();
    final subjects = _subjectsForExam(profile, exam);
    setState(() {
      _exam = exam.isEmpty ? null : exam;
      if (subjects.isNotEmpty) {
        _subjectCode = subjects.first.subjectCode;
      }
    });
  }

  List<UserSubjectEntity> _subjectsForExam(
    LearningProfileEntity profile,
    String? exam,
  ) {
    final active = profile.subjects.where((s) => s.isActive).toList();
    final e = (exam ?? '').toLowerCase();
    if (e.isEmpty) return active;
    final prefixes = e == 'yks'
        ? const {'tyt_', 'ayt_', 'yks_'}
        : {'${e}_'};
    final filtered = active
        .where((s) => prefixes.any((p) => s.subjectCode.toLowerCase().startsWith(p)))
        .toList();
    return filtered.isNotEmpty ? filtered : active;
  }

  List<String> _examOptions(LearningProfileEntity profile) {
    final types = profile.switchableExamTypes;
    if (types.isNotEmpty) return types;
    return profile.allowedExamTypes;
  }

  Future<void> _generate() async {
    final exam = _exam;
    final subject = _subjectCode;
    final topic = _topicCode;
    if (exam == null || exam.isEmpty) {
      setState(() => _error = 'Sınav seç.');
      return;
    }
    if (subject == null || subject.isEmpty) {
      setState(() => _error = 'Ders seç.');
      return;
    }
    if (topic == null || topic.isEmpty) {
      setState(() => _error = 'Konu seç.');
      return;
    }

    setState(() {
      _generating = true;
      _error = null;
    });

    try {
      String topicName = topic;
      if (_exam != null && _subjectCode != null) {
        final catalog = await ref.read(
          examCatalogTopicsProvider((
            exam: _exam!,
            subject: _subjectCode!,
          )).future,
        );
        for (final t in catalog) {
          if (t.code == topic) {
            topicName = t.name;
            break;
          }
        }
      }

      final quiz = await ref.read(topicQuizDatasourceProvider).generate(
            subjectCode: subject,
            topicCode: topic,
            count: _count,
            difficulty: _difficulty,
            examType: exam,
          );
      if (!mounted) return;
      context.push(
        '/quiz-session'
        '?subject_code=${Uri.encodeComponent(subject)}'
        '&topic_code=${Uri.encodeComponent(topic)}'
        '&topic_name=${Uri.encodeComponent(topicName)}'
        '&generation_id=${quiz.id}',
      );
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } catch (_) {
      if (!mounted) return;
      setState(() => _error = 'Soru üretilemedi. Tekrar dene.');
    } finally {
      if (mounted) setState(() => _generating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(learningProfileProvider);
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Soru Üret')),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(
          message: '$e',
          onRetry: () => invalidateLearningProfile(ref),
        ),
        data: (profile) {
          final exams = _examOptions(profile);
          final subjects = _subjectsForExam(profile, _exam);
          final topicsAsync = (_exam == null ||
                  _exam!.isEmpty ||
                  _subjectCode == null ||
                  _subjectCode!.isEmpty)
              ? const AsyncValue<List<({String code, String name})>>.data([])
              : ref.watch(
                  examCatalogTopicsProvider((
                    exam: _exam!,
                    subject: _subjectCode!,
                  )),
                );

          // Legacy fallback if exam-catalog empty
          final legacyTopics = (_subjectCode == null || _subjectCode!.isEmpty)
              ? const AsyncValue<List<TopicOption>>.data([])
              : ref.watch(subjectTopicsProvider(_subjectCode!));

          List<({String code, String name})> resolveTopics() {
            final c = topicsAsync.valueOrNull;
            if (c != null && c.isNotEmpty) return c;
            final legacy = legacyTopics.valueOrNull ?? const [];
            return [
              for (final t in legacy) (code: t.code, name: t.name),
            ];
          }

          return ListView(
            padding: AppSpacing.pageWide,
            children: [
              Text(
                'AI ile soru üret',
                style: text.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'Hazır konu testlerinden ayrıdır. Üretim Gemini/QIE ile yapılır.',
                style: text.bodyMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              Text('Sınav', style: text.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: AppSpacing.xs),
              DropdownButtonFormField<String>(
                value: exams.contains(_exam) ? _exam : null,
                decoration: const InputDecoration(border: OutlineInputBorder()),
                items: [
                  for (final e in exams)
                    DropdownMenuItem(value: e, child: Text(e.toUpperCase())),
                ],
                onChanged: _generating
                    ? null
                    : (v) => setState(() {
                          _exam = v;
                          final subs = _subjectsForExam(profile, v);
                          _subjectCode =
                              subs.isNotEmpty ? subs.first.subjectCode : null;
                          _topicCode = null;
                        }),
              ),
              const SizedBox(height: AppSpacing.md),

              Text('Ders', style: text.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: AppSpacing.xs),
              DropdownButtonFormField<String>(
                value: subjects.any((s) => s.subjectCode == _subjectCode)
                    ? _subjectCode
                    : null,
                decoration: const InputDecoration(border: OutlineInputBorder()),
                items: [
                  for (final s in subjects)
                    DropdownMenuItem(
                      value: s.subjectCode,
                      child: Text(s.subjectName),
                    ),
                ],
                onChanged: _generating
                    ? null
                    : (v) => setState(() {
                          _subjectCode = v;
                          _topicCode = null;
                        }),
              ),
              const SizedBox(height: AppSpacing.md),

              Text('Konu', style: text.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: AppSpacing.xs),
              (topicsAsync.isLoading || legacyTopics.isLoading)
                  ? const LinearProgressIndicator()
                  : Builder(
                      builder: (context) {
                        final topics = resolveTopics();
                        return DropdownButtonFormField<String>(
                          value: topics.any((t) => t.code == _topicCode)
                              ? _topicCode
                              : null,
                          decoration: const InputDecoration(
                            border: OutlineInputBorder(),
                          ),
                          items: [
                            for (final t in topics)
                              DropdownMenuItem(
                                value: t.code,
                                child: Text(t.name),
                              ),
                          ],
                          onChanged: (!_generating && _subjectCode != null)
                              ? (v) => setState(() => _topicCode = v)
                              : null,
                        );
                      },
                    ),
              const SizedBox(height: AppSpacing.md),

              Text('Soru sayısı', style: text.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: AppSpacing.xs),
              Wrap(
                spacing: AppSpacing.xs,
                children: [
                  for (final c in _counts)
                    ChoiceChip(
                      label: Text('$c'),
                      selected: _count == c,
                      onSelected: _generating
                          ? null
                          : (_) => setState(() => _count = c),
                    ),
                ],
              ),
              const SizedBox(height: AppSpacing.md),

              Text('Zorluk', style: text.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: AppSpacing.xs),
              Wrap(
                spacing: AppSpacing.xs,
                children: [
                  for (final e in const [
                    ('easy', 'Kolay'),
                    ('medium', 'Orta'),
                    ('hard', 'Zor'),
                  ])
                    ChoiceChip(
                      label: Text(e.$2),
                      selected: _difficulty == e.$1,
                      onSelected: _generating
                          ? null
                          : (_) => setState(() => _difficulty = e.$1),
                    ),
                ],
              ),
              const SizedBox(height: AppSpacing.xl),

              if (_error != null) ...[
                Text(
                  _error!,
                  style: text.bodyMedium?.copyWith(color: scheme.error),
                ),
                const SizedBox(height: AppSpacing.sm),
              ],

              FilledButton.icon(
                onPressed: _generating ? null : _generate,
                icon: _generating
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(StudyIcons.quiz),
                label: Text(_generating ? 'Üretiliyor…' : 'Soruları Üret'),
              ),
              if (_generating) ...[
                const SizedBox(height: AppSpacing.md),
                const LinearProgressIndicator(),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  'Soru üretimi biraz sürebilir. Lütfen bekle.',
                  style: text.bodySmall?.copyWith(
                    color: scheme.onSurfaceVariant,
                  ),
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}
