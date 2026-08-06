import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../educational_assets/presentation/components/eae_interactive_canvas.dart';
import '../../data/topic_quiz_remote_datasource.dart';

/// Sprint 14 — Topic Quiz Session (Secondary tool).
/// Soru Kaydı formu değil; üretilmiş quiz çözümü + Evidence.
class QuizSessionScreen extends ConsumerStatefulWidget {
  const QuizSessionScreen({
    super.key,
    required this.subjectCode,
    required this.topicCode,
    this.topicName,
    this.generationId,
  });

  final String subjectCode;
  final String topicCode;
  final String? topicName;
  final String? generationId;

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
    } else {
      await _generate();
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
        // Submitted quiz: items hide answers; show generate option via retry
        setState(() {
          _quiz = quiz;
          _loading = false;
          _error =
              'Bu quiz daha önce gönderildi. Yeni quiz üretmek için tekrar dene.';
        });
        return;
      }
      if (_looksLikeAuthorStub(quiz)) {
        // Eski offline stub kayıtlarını yeniden açma — taze üretim yap
        await _generate();
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

  Future<void> _generate() async {
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
      _answers.clear();
      _selectedNodes.clear();
      _index = 0;
    });
    try {
      final examType =
          ref.read(learningProfileProvider).valueOrNull?.activeExamType;
      final quiz = await ref.read(topicQuizDatasourceProvider).generate(
            subjectCode: widget.subjectCode,
            topicCode: widget.topicCode,
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
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              FilledButton(onPressed: _generate, child: const Text('Tekrar dene')),
            ],
          ),
        ),
      );
    }
    if (_result != null) {
      return _ResultsView(result: _result!, onRetry: _generate);
    }
    final quiz = _quiz;
    if (quiz == null || quiz.items.isEmpty) {
      return Center(
        child: FilledButton(onPressed: _generate, child: const Text('Soru üret')),
      );
    }
    final item = quiz.items[_index.clamp(0, quiz.items.length - 1)];
    final selected = _answers[item.id];

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
          child: Row(
            children: [
              Text(
                'Soru ${_index + 1} / ${quiz.items.length}',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const Spacer(),
              Text(
                'Doğru cevaplar gizli',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                item.stem,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 16),
              if (item.targetAssetId != null && item.targetAssetId!.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: EAEInteractiveCanvas(
                    targetAssetId: item.targetAssetId!,
                    selectedNodeId: _selectedNodes[item.id],
                    onNodeSelected: (nodeId) {
                      setState(() {
                        _selectedNodes[item.id] = nodeId;
                        // Map node id / label onto A-D choice when possible
                        for (final entry in item.choices.entries) {
                          final text = entry.value;
                          if (text == nodeId ||
                              text.contains(nodeId) ||
                              nodeId.endsWith('::${text.toLowerCase().replaceAll(' ', '_')}') ||
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
              ...['A', 'B', 'C', 'D'].map((key) {
                final text = item.choices[key] ?? '';
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: RadioListTile<String>(
                    value: key,
                    groupValue: selected,
                    onChanged: (v) => setState(() => _answers[item.id] = v),
                    title: Text('$key) $text'),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(
                        color: Theme.of(context).colorScheme.outlineVariant,
                      ),
                    ),
                  ),
                );
              }),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              if (_index > 0)
                OutlinedButton(
                  onPressed: () => setState(() => _index -= 1),
                  child: const Text('Önceki'),
                ),
              const Spacer(),
              if (_index < quiz.items.length - 1)
                FilledButton(
                  onPressed: () => setState(() => _index += 1),
                  child: const Text('Sonraki'),
                )
              else
                FilledButton(
                  onPressed: _submitting ? null : _submit,
                  child: _submitting
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Bitir'),
                ),
            ],
          ),
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
                          item.stem,
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Senin: ${item.selectedKey ?? "—"} · Doğru: ${item.correctKey}',
                  ),
                  if (item.targetAssetId != null && item.targetAssetId!.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 12.0, bottom: 8.0),
                      child: EAEInteractiveCanvas(
                        targetAssetId: item.targetAssetId!,
                        correctNodeId: item.correctNodeId,
                        showAnswer: true,
                        onNodeSelected: (_) {},
                      ),
                    ),
                  if (item.explanation != null && item.explanation!.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      item.explanation!,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 8),
        FilledButton(onPressed: onRetry, child: const Text('Yeni quiz üret')),
      ],
    );
  }
}
