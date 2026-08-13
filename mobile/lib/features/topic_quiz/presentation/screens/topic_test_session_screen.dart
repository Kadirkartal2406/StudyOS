import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/utils/math_display_text.dart';
import '../../../../core/widgets/app_error_view.dart';
import '../../../../shared/widgets/study_question_chrome.dart';
import '../../data/topic_test_remote_datasource.dart';

/// Solve a published catalog test — DB only, no Gemini.
class TopicTestSessionScreen extends ConsumerStatefulWidget {
  const TopicTestSessionScreen({
    super.key,
    required this.testId,
    this.subjectCode,
    this.topicCode,
    this.topicName,
  });

  final String testId;
  final String? subjectCode;
  final String? topicCode;
  final String? topicName;

  @override
  ConsumerState<TopicTestSessionScreen> createState() =>
      _TopicTestSessionScreenState();
}

class _TopicTestSessionScreenState
    extends ConsumerState<TopicTestSessionScreen> {
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  TopicTestAttempt? _attempt;
  TopicTestSubmitResult? _result;
  final Map<String, String?> _answers = {};
  int _index = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _start());
  }

  Future<void> _start() async {
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
      _answers.clear();
      _index = 0;
    });
    try {
      final attempt =
          await ref.read(topicTestDatasourceProvider).start(widget.testId);
      if (!mounted) return;
      setState(() {
        _attempt = attempt;
        _loading = false;
      });
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.message;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Test başlatılamadı.';
        _loading = false;
      });
    }
  }

  Future<void> _submit() async {
    final attempt = _attempt;
    if (attempt == null || _submitting) return;
    setState(() => _submitting = true);
    try {
      final result = await ref.read(topicTestDatasourceProvider).submit(
            attemptId: attempt.attemptId,
            answers: {
              for (final it in attempt.items) it.id: _answers[it.id],
            },
          );
      if (!mounted) return;
      setState(() {
        _result = result;
        _submitting = false;
      });
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.message;
        _submitting = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Gönderilemedi.';
        _submitting = false;
      });
    }
  }

  List<String> _choiceKeys(Map<String, String> choices) {
    const order = ['A', 'B', 'C', 'D', 'E'];
    final keys = choices.keys.map((k) => k.toUpperCase()).toSet();
    return [
      for (final k in order)
        if (keys.contains(k)) k,
      ...keys.where((k) => !order.contains(k)),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final title = widget.topicName ?? 'Konu Testi';
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: _buildBody(context),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null && _attempt == null) {
      return AppErrorView(message: _error!, onRetry: _start);
    }
    final result = _result;
    if (result != null) {
      return ListView(
        padding: AppSpacing.pageWide,
        children: [
          Text(
            'Sonuç: %${result.accuracyPct.round()}',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Doğru ${result.correctCount} · Yanlış ${result.wrongCount} · '
            'Boş ${result.blankCount}',
          ),
          const SizedBox(height: AppSpacing.lg),
          for (final r in result.reviewItems)
            Card(
              margin: const EdgeInsets.only(bottom: AppSpacing.sm),
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${r.ordIndex + 1}. ${mathDisplayText(r.stem)}',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Senin: ${r.selectedKey ?? '—'} · Doğru: ${r.correctKey}',
                      style: TextStyle(
                        color: r.isCorrect == true
                            ? AppColors.success
                            : AppColors.error,
                      ),
                    ),
                    if (r.explanation != null && r.explanation!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(mathDisplayText(r.explanation!)),
                      ),
                  ],
                ),
              ),
            ),
        ],
      );
    }

    final attempt = _attempt!;
    final items = attempt.items;
    if (items.isEmpty) {
      return const Center(child: Text('Sorular bulunamadı'));
    }
    final item = items[_index.clamp(0, items.length - 1)];
    final selected = _answers[item.id];

    return Column(
      children: [
        StudyQuestionProgress(
          current: _index + 1,
          total: items.length,
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.md,
              AppSpacing.sm,
              AppSpacing.md,
              AppSpacing.lg,
            ),
            children: [
              Text(
                mathDisplayText(item.stem),
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontSize: 17,
                      height: 1.5,
                      fontWeight: FontWeight.w500,
                    ),
              ),
              const SizedBox(height: AppSpacing.xl),
              ..._choiceKeys(item.choices).map((key) {
                return StudyChoiceOption(
                  letter: key,
                  label: mathDisplayText(item.choices[key]),
                  selected: selected == key,
                  onTap: () => setState(() => _answers[item.id] = key),
                );
              }),
            ],
          ),
        ),
        StudyQuestionFooter(
          canGoPrevious: _index > 0,
          isLast: _index >= items.length - 1,
          submitting: _submitting,
          onPrevious: () => setState(() => _index -= 1),
          onNext: () => setState(() => _index += 1),
          onSubmit: _submit,
        ),
      ],
    );
  }
}
