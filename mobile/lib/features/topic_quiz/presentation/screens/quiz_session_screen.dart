import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/app_config.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/utils/math_display_text.dart';
import '../../../../core/widgets/app_error_view.dart';
import '../../../../shared/widgets/study_question_chrome.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../educational_assets/presentation/components/eae_interactive_canvas.dart';
import '../../data/topic_quiz_remote_datasource.dart';

/// AI-generated topic quiz session (from Menü → Soru Üret).
/// Not used for published Topic Test Catalog (those use TopicTestSessionScreen).
class QuizSessionScreen extends ConsumerStatefulWidget {
  const QuizSessionScreen({
    super.key,
    required this.subjectCode,
    required this.topicCode,
    this.topicName,
    this.generationId,
    this.count,
    this.difficulty,
    this.examType,
    this.allowGenerate = false,
  });

  final String subjectCode;
  final String topicCode;
  final String? topicName;
  final String? generationId;
  final int? count;
  final String? difficulty;
  final String? examType;
  /// When true (explicit), may call Gemini generate. Topic pages must leave false.
  final bool allowGenerate;

  @override
  ConsumerState<QuizSessionScreen> createState() => _QuizSessionScreenState();
}

class _QuizSessionScreenState extends ConsumerState<QuizSessionScreen> {
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  QuizGenerationEntity? _quiz;
  QuizSubmitResultEntity? _result;
  final Map<String, String?> _answers = {};
  final Map<String, String?> _selectedNodes = {};
  int _index = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    final existing = widget.generationId;
    if (existing != null && existing.isNotEmpty) {
      await _loadExisting(existing);
    } else if (widget.allowGenerate) {
      await _generate();
    } else {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error =
            'Soru üretmek için Menü → Soru Üret kullan. '
            'Hazır testler için Konu Testleri’ne git.';
      });
    }
  }

  Future<void> _loadExisting(String generationId) async {
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
      _answers.clear();
      _selectedNodes.clear();
      _index = 0;
    });
    try {
      final quiz =
          await ref.read(topicQuizDatasourceProvider).get(generationId);
      if (!mounted) return;
      if (quiz.status == 'submitted') {
        if (!mounted) return;
        setState(() {
          _quiz = null;
          _loading = false;
          _error =
              'Bu quiz daha önce gönderildi. Yeni üretim için Menü → Soru Üret.';
        });
        return;
      }
      if (_looksLikeAuthorStub(quiz)) {
        if (widget.allowGenerate) {
          await _generate();
          return;
        }
        if (!mounted) return;
        setState(() {
          _quiz = null;
          _loading = false;
          _error = 'Bu kayıt geçersiz. Menü → Soru Üret ile yeni soru üret.';
        });
        return;
      }
      setState(() {
        _quiz = quiz;
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
        _error = 'Quiz yüklenemedi.';
        _loading = false;
      });
    }
  }

  bool _looksLikeAuthorStub(QuizGenerationEntity quiz) {
    for (final item in quiz.items) {
      final stem = item.stem.toLowerCase();
      if (stem.contains('bloom düzeyi') ||
          stem.contains('ölçülen kazanım') ||
          stem.contains('kelimelik resmi bir üslup') ||
          stem.contains('günlük yaşamdan bir durumu anlatan kısa bir metin')) {
        return true;
      }
      final choices = item.choices.values.map((e) => e.toLowerCase()).join(' ');
      if (choices.contains('doğru yanıt') && choices.contains('çeldirici')) {
        return true;
      }
    }
    return false;
  }

  List<String> _choiceKeys(Map<String, String> choices) {
    const order = ['A', 'B', 'C', 'D', 'E'];
    final present = [
      for (final key in order)
        if ((choices[key] ?? '').trim().isNotEmpty) key,
    ];
    if (present.isNotEmpty) return present;
    return order;
  }

  Future<void> _generate() async {
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
      _quiz = null;
      _answers.clear();
      _selectedNodes.clear();
      _index = 0;
    });
    try {
      final examType = widget.examType ??
          ref.read(learningProfileProvider).valueOrNull?.activeExamType;
      final quiz = await ref.read(topicQuizDatasourceProvider).generate(
            subjectCode: widget.subjectCode,
            topicCode: widget.topicCode,
            count: widget.count ?? AppConfig.topicQuizDefaultCount,
            difficulty: widget.difficulty ?? 'medium',
            examType: examType,
          );
      if (!mounted) return;
      setState(() {
        _quiz = quiz;
        _loading = false;
      });
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.message;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Soru üretilemedi. Tekrar deneyin.';
        _loading = false;
      });
    }
  }

  Future<void> _submit() async {
    final quiz = _quiz;
    if (quiz == null) return;
    setState(() => _submitting = true);
    try {
      final result = await ref.read(topicQuizDatasourceProvider).submit(
            generationId: quiz.id,
            answers: {
              for (final item in quiz.items) item.id: _answers[item.id],
            },
            selectedNodes: {
              for (final item in quiz.items)
                if (_selectedNodes[item.id] != null)
                  item.id: _selectedNodes[item.id],
            },
          );
      if (!mounted) return;
      setState(() {
        _result = result;
        _submitting = false;
      });
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message)),
      );
    } catch (_) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Gönderim başarısız')),
      );
    }
  }

  void _retryOrSoruUret() {
    if (widget.allowGenerate) {
      _generate();
      return;
    }
    context.push('/soru-uret');
  }

  @override
  Widget build(BuildContext context) {
    final title = widget.topicName ?? _quiz?.topicName ?? widget.topicCode;
    return Scaffold(
      appBar: AppBar(
        title: Text('Quiz · $title'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/subjects');
            }
          },
        ),
      ),
      body: SafeArea(child: _buildBody(context)),
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Sorular üretiliyor ve kontrol ediliyor…'),
          ],
        ),
      );
    }
    if (_error != null) {
      return AppErrorView(
        message: _error!,
        onRetry: _retryOrSoruUret,
      );
    }
    if (_result != null) {
      return _ResultsView(result: _result!, onRetry: _retryOrSoruUret);
    }
    final quiz = _quiz;
    if (quiz == null || quiz.items.isEmpty) {
      return AppErrorView(
        message: 'Gösterilecek soru yok. Menü → Soru Üret ile yeni üret.',
        onRetry: _retryOrSoruUret,
      );
    }
    final item = quiz.items[_index.clamp(0, quiz.items.length - 1)];
    final selected = _answers[item.id];

    return Column(
      children: [
        StudyQuestionProgress(
          current: _index + 1,
          total: quiz.items.length,
          trailing: Text(
            'Doğru cevaplar gizli',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
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
                '${_index + 1}.',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                mathDisplayText(item.stem),
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontSize: 17,
                      height: 1.5,
                      fontWeight: FontWeight.w500,
                      color: Theme.of(context).brightness == Brightness.dark
                          ? const Color(0xFFF8FAFC)
                          : AppColors.textPrimary,
                    ),
              ),
              const SizedBox(height: AppSpacing.xl),
              if (item.eaeInteraction != null &&
                  item.eaeInteraction!['asset_uri'] != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.lg),
                  child: EAEInteractiveCanvas(
                    targetAssetId: item.eaeInteraction!['asset_uri'] as String,
                    selectedNodeId: _selectedNodes[item.id],
                    onNodeSelected: (nodeId) {
                      setState(() {
                        _selectedNodes[item.id] = nodeId;
                        for (final entry in item.choices.entries) {
                          final text = entry.value;
                          if (text == nodeId ||
                              text.contains(nodeId) ||
                              nodeId.endsWith(
                                  '::${text.toLowerCase().replaceAll(' ', '_')}') ||
                              nodeId.split('::').last ==
                                  text
                                      .toLowerCase()
                                      .replaceAll('ı', 'i')
                                      .replaceAll('ğ', 'g')
                                      .replaceAll('ü', 'u')
                                      .replaceAll('ş', 's')
                                      .replaceAll('ö', 'o')
                                      .replaceAll('ç', 'c')
                                      .replaceAll(' ', '_')) {
                            _answers[item.id] = entry.key;
                            break;
                          }
                        }
                      });
                    },
                  ),
                ),
              if (item.eaeInteraction == null)
                ..._choiceKeys(item.choices).map((key) {
                  final choiceText = mathDisplayText(item.choices[key]);
                  return StudyChoiceOption(
                    letter: key,
                    label: choiceText,
                    selected: selected == key,
                    onTap: () => setState(() => _answers[item.id] = key),
                  );
                }),
            ],
          ),
        ),
        StudyQuestionFooter(
          canGoPrevious: _index > 0,
          isLast: _index >= quiz.items.length - 1,
          submitting: _submitting,
          onPrevious: () => setState(() => _index -= 1),
          onNext: () => setState(() => _index += 1),
          onSubmit: _submit,
        ),
      ],
    );
  }
}

class _ResultsView extends StatelessWidget {
  const _ResultsView({required this.result, required this.onRetry});

  final QuizSubmitResultEntity result;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Sonuç: %${result.accuracyPct.toStringAsFixed(0)}',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 8),
        Text(
          'Doğru ${result.correctCount} · Yanlış ${result.wrongCount} · Boş ${result.blankCount}',
        ),
        const SizedBox(height: 16),
        ...result.reviewItems.map((item) {
          final ok = item.isCorrect == true;
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        ok ? Icons.check_circle : Icons.cancel,
                        color: ok ? Colors.green : Colors.redAccent,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          mathDisplayText(item.stem),
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Senin: ${item.selectedKey ?? "—"} · Doğru: ${item.correctKey}',
                  ),
                  if (item.eaeInteraction != null && item.eaeInteraction!['asset_uri'] != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12.0, bottom: 8.0),
                      child: EAEInteractiveCanvas(
                        targetAssetId: item.eaeInteraction!['asset_uri'] as String,
                        correctNodeId: item.eaeInteraction!['expected_node_id'] as String?,
                        showAnswer: true,
                        onNodeSelected: (_) {},
                      ),
                    ),
                  if (item.explanation != null && item.explanation!.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      mathDisplayText(item.explanation),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 8),
        FilledButton(onPressed: onRetry, child: const Text('Soru Üret’e git')),
      ],
    );
  }
}
