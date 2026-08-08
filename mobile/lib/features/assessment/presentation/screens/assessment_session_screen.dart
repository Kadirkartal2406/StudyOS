import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../onboarding/presentation/providers/first_run_phase_provider.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../data/assessment_remote_datasource.dart';
import '../utils/level_test_count.dart';
import '../utils/pdf_download.dart';
import '../widgets/math_scratch_pad.dart';
import '../widgets/simple_calculator.dart';

/// Sprint 18 — Assessment session (Sense). Topic Quiz UI kalıbı; Decision yok.
class AssessmentSessionScreen extends ConsumerStatefulWidget {
  const AssessmentSessionScreen({
    super.key,
    this.sessionId,
    this.bootstrap,
    this.subjectCode,
    this.fromSetup = false,
    this.questionCount,
  });

  /// Mevcut session id.
  final String? sessionId;

  /// `daily` | `branch` | `calibration` — id yoksa start çağırır.
  final String? bootstrap;
  final String? subjectCode;

  /// RC3 — ilk kullanım seviye testi; bitince sıradaki derse / preparing.
  final bool fromSetup;

  /// Seviye testi soru sayısı (sınava göre).
  final int? questionCount;

  @override
  ConsumerState<AssessmentSessionScreen> createState() =>
      _AssessmentSessionScreenState();
}

class _AssessmentSessionScreenState
    extends ConsumerState<AssessmentSessionScreen> {
  bool _loading = true;
  bool _submitting = false;
  String? _error;
  AssessmentSessionEntity? _session;
  AssessmentSubmitResultEntity? _result;
  final Map<String, String?> _answers = {};
  int _index = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    final existing = widget.sessionId;
    if (existing != null && existing.isNotEmpty) {
      await _load(existing);
      return;
    }
    await _start();
  }

  Future<void> _load(String sessionId) async {
    setState(() {
      _loading = true;
      _error = null;
      _result = null;
      _answers.clear();
      _index = 0;
    });
    try {
      final session =
          await ref.read(assessmentDatasourceProvider).getSession(sessionId);
      if (!mounted) return;
      if (session.status == 'submitted') {
        setState(() {
          _session = session;
          _loading = false;
          _error = 'Bu assessment zaten gönderildi.';
        });
        return;
      }
      setState(() {
        _session = session;
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
        _error = 'Assessment yüklenemedi.';
        _loading = false;
      });
    }
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
      final ds = ref.read(assessmentDatasourceProvider);
      final mode = widget.bootstrap ?? 'daily';
      late AssessmentSessionEntity session;
      if (mode == 'daily') {
        session = await ds.startDaily();
      } else if (mode == 'branch') {
        final code = widget.subjectCode;
        if (code == null || code.isEmpty) {
          throw const UnknownException(message: 'Ders kodu gerekli');
        }
        session = await ds.start(kind: 'branch_question', subjectCode: code);
      } else {
        final code = widget.subjectCode;
        if (code == null || code.isEmpty) {
          throw const UnknownException(message: 'Ders kodu gerekli');
        }
        final profile = ref.read(learningProfileProvider).valueOrNull;
        final exam =
            profile?.activeExamType ?? profile?.primaryExamType ?? 'kpss';
        final count =
            widget.questionCount ?? levelTestCountForExam(exam);
        session = await ds.start(
          kind: 'initial_calibration',
          subjectCode: code,
          count: count,
        );
      }
      if (!mounted) return;
      setState(() {
        _session = session;
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
        _error = 'Assessment başlatılamadı.';
        _loading = false;
      });
    }
  }

  Future<void> _submit() async {
    final session = _session;
    if (session == null) return;
    setState(() => _submitting = true);
    try {
      final result = await ref.read(assessmentDatasourceProvider).submit(
            sessionId: session.id,
            answers: {
              for (final q in session.questions) q.id: _answers[q.id],
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

  void _showQuestionNavigator() {
    if (_session == null) return;
    
    // Group questions by subject
    final subjects = <String, List<int>>{};
    for (var i = 0; i < _session!.questions.length; i++) {
      final q = _session!.questions[i];
      final subj = q.subjectName ?? 'Genel';
      subjects.putIfAbsent(subj, () => []).add(i);
    }
    
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.6,
          minChildSize: 0.4,
          maxChildSize: 0.9,
          builder: (_, controller) {
            final totalCount = _session!.questions.length;
            final answeredCount = _answers.keys.length;
            final emptyCount = totalCount - answeredCount;
            
            return Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text(
                        'Deneme İstatistikleri',
                        style: Theme.of(ctx).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _StatChip(label: 'Toplam', count: totalCount, color: Colors.blue),
                          _StatChip(label: 'Çözülen', count: answeredCount, color: Colors.green),
                          _StatChip(label: 'Boş', count: emptyCount, color: Colors.orange),
                        ],
                      ),
                    ],
                  ),
                ),
                const Divider(),
                Expanded(
                  child: ListView.builder(
                    controller: controller,
                    itemCount: subjects.length,
                    itemBuilder: (context, index) {
                      final subj = subjects.keys.elementAt(index);
                      final indices = subjects[subj]!;
                      
                      int subjAnswered = 0;
                      for (final i in indices) {
                        final qId = _session!.questions[i].id;
                        if (_answers.containsKey(qId) && _answers[qId] != null) {
                          subjAnswered++;
                        }
                      }
                      
                      return Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  subj,
                                  style: Theme.of(context).textTheme.titleMedium,
                                ),
                                Text(
                                  '$subjAnswered / ${indices.length} Çözüldü',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: indices.map((idx) {
                                final isCurrent = idx == _index;
                                final isAnswered = _answers.containsKey(_session!.questions[idx].id) && 
                                                  _answers[_session!.questions[idx].id] != null;
                                
                                return InkWell(
                                  onTap: () {
                                    Navigator.pop(ctx);
                                    setState(() => _index = idx);
                                  },
                                  child: Container(
                                    width: 40,
                                    height: 40,
                                    alignment: Alignment.center,
                                    decoration: BoxDecoration(
                                      color: isCurrent 
                                          ? Theme.of(context).colorScheme.primary 
                                          : (isAnswered ? Colors.green.withOpacity(0.2) : Theme.of(context).colorScheme.surfaceContainerHighest),
                                      borderRadius: BorderRadius.circular(8),
                                      border: isCurrent ? null : Border.all(
                                        color: isAnswered ? Colors.green : Colors.transparent,
                                      ),
                                    ),
                                    child: Text(
                                      '${idx + 1}',
                                      style: TextStyle(
                                        color: isCurrent 
                                            ? Theme.of(context).colorScheme.onPrimary 
                                            : (isAnswered ? Colors.green[700] : null),
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                );
                              }).toList(),
                            ),
                            const SizedBox(height: 16),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  String get _title {
    final s = _session;
    if (s == null) return 'Assessment';
    return switch (s.kind) {
      'daily_challenge' => 'Günün Denemesi',
      'branch_question' => 'Branş Sorusu',
      _ => 'Seviye testi',
    };
  }

  Future<void> _continueAfterSetup() async {
    final ds = ref.read(assessmentDatasourceProvider);
    try {
      final overview = await ds.overview();
      AssessmentProgressItemEntity? next;
      for (final s in overview.subjects) {
        if (!s.completed) {
          next = s;
          break;
        }
      }
      if (!mounted) return;
      if (next != null) {
        final profile = ref.read(learningProfileProvider).valueOrNull;
        final exam =
            profile?.activeExamType ?? profile?.primaryExamType ?? 'kpss';
        final count =
            widget.questionCount ?? levelTestCountForExam(exam);
        context.go(
          '/assessment/branch/start'
          '?subject_code=${Uri.encodeComponent(next.subjectCode)}'
          '&kind=calibration'
          '&setup=1'
          '&count=$count',
        );
        return;
      }
    } catch (_) {}
    await ref.read(firstRunPhaseProvider.notifier).setPhase('preparing');
    if (!mounted) return;
    context.go('/setup/preparing');
  }

  @override
  Widget build(BuildContext context) {
    final q = (_session != null &&
            _session!.questions.isNotEmpty &&
            _index < _session!.questions.length)
        ? _session!.questions[_index]
        : null;
    final subtitle = q?.subjectName ?? _session?.subjectName;
    final showMath = q?.isMathSubject == true;
    return Scaffold(
      appBar: AppBar(
        title: Text(subtitle == null ? _title : '$_title · $subtitle'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/dashboard');
            }
          },
        ),
        actions: [
            IconButton(
              tooltip: 'Sorular & İstatistikler',
              icon: const Icon(Icons.grid_view_outlined),
              onPressed: _showQuestionNavigator,
            ),
          if (showMath)
            IconButton(
              tooltip: 'Hesap makinesi',
              icon: const Icon(Icons.calculate_outlined),
              onPressed: () => SimpleCalculatorSheet.show(context),
            ),
        ],
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
            Text('Sorular hazırlanıyor…'),
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
              FilledButton(
                onPressed: widget.sessionId != null
                    ? () => _load(widget.sessionId!)
                    : _start,
                child: const Text('Tekrar dene'),
              ),
            ],
          ),
        ),
      );
    }
    if (_result != null) {
      final isDaily = _session?.kind == 'daily_challenge' ||
          widget.bootstrap == 'daily';
      final rawCode = widget.subjectCode ?? _session?.subjectCode;
      final subjectCode =
          (rawCode == null || rawCode == 'booklet') ? null : rawCode;
      return _ResultsView(
        result: _result!,
        showLeaderboard: isDaily,
        subjectCode: subjectCode,
        doneLabel: widget.fromSetup ? 'Sonraki derse geç' : 'Tamam',
        onDone: () async {
          if (widget.fromSetup) {
            await _continueAfterSetup();
            return;
          }
          if (context.canPop()) {
            context.pop();
          } else {
            context.go('/assessment');
          }
        },
        onLeaderboard: isDaily
            ? () {
                final q = subjectCode != null && subjectCode.isNotEmpty
                    ? '?subject_code=$subjectCode'
                    : '';
                context.push('/assessment/daily/leaderboard$q');
              }
            : null,
      );
    }
    final session = _session;
    if (session == null || session.questions.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                session == null
                    ? 'Deneme henüz başlamadı'
                    : 'Bu oturumda soru yok — yeniden üretilecek',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: _submitting ? null : _start,
                child: const Text('Soruları yükle'),
              ),
            ],
          ),
        ),
      );
    }
    final item = session.questions[_index.clamp(0, session.questions.length - 1)];
    final selected = _answers[item.id];
    final showMath = item.isMathSubject;
    final wide = MediaQuery.sizeOf(context).width >= 900;

    final questionPane = Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  'Soru ${_index + 1} / ${session.questions.length}'
                  '${item.subjectName != null ? ' · ${item.subjectName}' : ''}',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
              ),
              if (showMath && !wide)
                TextButton.icon(
                  onPressed: () {
                    showModalBottomSheet<void>(
                      context: context,
                      isScrollControlled: true,
                      builder: (_) => SizedBox(
                        height: MediaQuery.sizeOf(context).height * 0.45,
                        child: const Padding(
                          padding: EdgeInsets.all(12),
                          child: MathScratchPad(),
                        ),
                      ),
                    );
                  },
                  icon: const Icon(Icons.draw_outlined, size: 18),
                  label: const Text('Çizim'),
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
              ...['A', 'B', 'C', 'D', 'E'].where((k) => item.choices.containsKey(k)).map((key) {
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
              if (_index < session.questions.length - 1)
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

    if (!showMath || !wide) {
      return questionPane;
    }

    return Row(
      children: [
        Expanded(flex: 3, child: questionPane),
        const VerticalDivider(width: 1),
        Expanded(
          flex: 2,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                Align(
                  alignment: Alignment.centerRight,
                  child: IconButton(
                    tooltip: 'Hesap makinesi',
                    onPressed: () => SimpleCalculatorSheet.show(context),
                    icon: const Icon(Icons.calculate_outlined),
                  ),
                ),
                const Expanded(child: MathScratchPad()),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _ResultsView extends ConsumerStatefulWidget {
  const _ResultsView({
    required this.result,
    required this.onDone,
    this.showLeaderboard = false,
    this.subjectCode,
    this.onLeaderboard,
    this.doneLabel = 'Tamam',
  });

  final AssessmentSubmitResultEntity result;
  final VoidCallback onDone;
  final bool showLeaderboard;
  final String? subjectCode;
  final VoidCallback? onLeaderboard;
  final String doneLabel;

  @override
  ConsumerState<_ResultsView> createState() => _ResultsViewState();
}

class _ResultsViewState extends ConsumerState<_ResultsView> {
  final Map<String, String> _explains = {};
  final Set<String> _loadingExplain = {};
  bool _reportBusy = false;

  Future<void> _downloadReport() async {
    final sessionId = widget.result.session.id;
    setState(() => _reportBusy = true);
    try {
      final bytes = await ref
          .read(assessmentDatasourceProvider)
          .downloadSessionReportPdf(sessionId);
      final path = await savePdfBytes(bytes, 'assessment-rapor.pdf');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(path == null ? 'Rapor indirildi' : 'Rapor: $path')),
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is AppException ? e.message : 'Rapor indirilemedi';
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } finally {
      if (mounted) setState(() => _reportBusy = false);
    }
  }

  Future<void> _loadExplain(AssessmentReviewItem item) async {
    if (_loadingExplain.contains(item.id) || _explains.containsKey(item.id)) {
      return;
    }
    setState(() => _loadingExplain.add(item.id));
    try {
      final data = await ref.read(assessmentDatasourceProvider).explainWrong(
            sessionId: widget.result.session.id,
            questionId: item.id,
            selectedKey: item.selectedKey,
          );
      final buf = StringBuffer(data.explanation);
      if (data.whyWrong != null && data.whyWrong!.isNotEmpty) {
        buf.writeln();
        buf.write('Neden yanlış: ${data.whyWrong}');
      }
      if (data.whyCorrect != null && data.whyCorrect!.isNotEmpty) {
        buf.writeln();
        buf.write('Neden doğru: ${data.whyCorrect}');
      }
      if (!mounted) return;
      setState(() => _explains[item.id] = buf.toString());
    } catch (e) {
      if (!mounted) return;
      final msg = e is AppException ? e.message : 'Açıklama alınamadı';
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } finally {
      if (mounted) {
        setState(() => _loadingExplain.remove(item.id));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final result = widget.result;
    final acc = result.session.accuracy;
    final pct = acc == null ? 0.0 : acc * 100;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Sonuç: %${pct.toStringAsFixed(0)}',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 8),
        Text(result.commentary),
        
        if (result.session.studyosScore != null) ...[
          const SizedBox(height: 16),
          if (result.session.isOfficial == false)
            Container(
              padding: const EdgeInsets.all(8),
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                "Bu sonuç tahminidir. Denemeyi saat 21:59'dan sonra çözdüğünüz için resmi sıralamaya dahil edilmediniz.",
                style: TextStyle(color: Colors.orange, fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ),
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      const Text('StudyOS Puanı', style: TextStyle(fontSize: 12, color: Colors.grey)),
                      const SizedBox(height: 4),
                      Text(
                        result.session.studyosScore!.toStringAsFixed(1),
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.purple.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      const Text('Sıralama', style: TextStyle(fontSize: 12, color: Colors.grey)),
                      const SizedBox(height: 4),
                      Text(
                        result.session.studyosRank != null ? '#${result.session.studyosRank}' : '--',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.purple),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],

        if (result.session.osymEstimations != null && result.session.osymEstimations!.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            'ÖSYM Tahmini Puanları',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ...result.session.osymEstimations!.entries.map((e) {
            final data = e.value as Map<String, dynamic>? ?? {};
            final s = data['score'] as num?;
            final r = data['rank'] as int?;
            return Padding(
              padding: const EdgeInsets.only(bottom: 4.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('YKS ${e.key}'),
                  Text('${s?.toStringAsFixed(2) ?? "--"} Puan ${r != null ? "(#$r)" : ""}'),
                ],
              ),
            );
          }),
        ],

        if (result.net != null) ...[
          const SizedBox(height: 16),
          Text(
            'Net: ${result.net!.toStringAsFixed(2)}'
            '${result.scoreFormula != null ? ' · ${result.scoreFormula}' : ''}',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
        ],
        if (result.estimatedSuccessPct != null) ...[
          const SizedBox(height: 8),
          Text(
            'Tahmini başarı: %${result.estimatedSuccessPct!.toStringAsFixed(0)}',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: _reportBusy ? null : _downloadReport,
          icon: _reportBusy
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.picture_as_pdf_outlined),
          label: const Text('Sonuç raporu (PDF)'),
        ),
        if (result.bySubject.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            'Ders bazlı',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          ...result.bySubject.map(
            (s) => ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              title: Text(s.subjectName),
              subtitle: Text(
                '${s.correct}D · ${s.wrong}Y · ${s.blank}B · Net ${s.net.toStringAsFixed(2)}',
              ),
            ),
          ),
        ],
        if (result.byTopic.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(
            'Konu bazlı',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          ...result.byTopic.take(20).map(
                (t) => ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text(t.topicName),
                  subtitle: Text('${t.correct}D · ${t.wrong}Y · ${t.blank}B'),
                ),
              ),
        ],
        if (widget.showLeaderboard && widget.onLeaderboard != null) ...[
          const SizedBox(height: 16),
          FilledButton.tonalIcon(
            onPressed: widget.onLeaderboard,
            icon: const Icon(Icons.leaderboard_outlined),
            label: Text(
              widget.subjectCode != null && widget.subjectCode!.isNotEmpty
                  ? 'Ders sıralamasını gör'
                  : 'Sıralamayı gör',
            ),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () => context.push('/assessment/daily/leaderboard'),
            icon: const Icon(Icons.public),
            label: const Text('Genel sıralama'),
          ),
        ],
        const SizedBox(height: 16),
        ...result.reviewItems.map((item) {
          final ok = item.isCorrect == true;
          final explainText = _explains[item.id] ?? item.explanation;
          final canExplain = !ok;
          final loading = _loadingExplain.contains(item.id);
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
                  if (explainText != null && explainText.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      explainText,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                  if (canExplain) ...[
                    const SizedBox(height: 8),
                    TextButton.icon(
                      onPressed: loading || _explains.containsKey(item.id)
                          ? null
                          : () => _loadExplain(item),
                      icon: loading
                          ? const SizedBox(
                              width: 14,
                              height: 14,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.lightbulb_outline, size: 18),
                      label: Text(
                        _explains.containsKey(item.id)
                            ? 'Açıklandı'
                            : 'Neden yanlış?',
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 8),
        FilledButton(onPressed: widget.onDone, child: Text(widget.doneLabel)),
      ],
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final int count;
  final Color color;
  const _StatChip({required this.label, required this.count, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(count.toString(), style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color)),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[700])),
      ],
    );
  }
}

