import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/ds.dart';
import '../../data/assessment_remote_datasource.dart';

/// Sprint 23 — Optik form: PDF sonrası cevap girişi.
class DailyOpticalScreen extends ConsumerStatefulWidget {
  const DailyOpticalScreen({super.key, required this.sessionId});

  final String sessionId;

  @override
  ConsumerState<DailyOpticalScreen> createState() => _DailyOpticalScreenState();
}

class _DailyOpticalScreenState extends ConsumerState<DailyOpticalScreen> {
  AssessmentSessionEntity? _session;
  final Map<String, String?> _answers = {};
  String? _error;
  bool _loading = true;
  bool _submitting = false;

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
      final session = await ref
          .read(assessmentDatasourceProvider)
          .getSession(widget.sessionId);
      if (!mounted) return;
      if (session.status == 'submitted') {
        setState(() {
          _session = session;
          _loading = false;
          _error = 'Bu deneme zaten gönderildi.';
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
        _error = 'Oturum yüklenemedi';
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
      final netLine = result.net != null
          ? 'Net ${result.net!.toStringAsFixed(2)}'
          : 'kaydedildi';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Optik gönderildi · $netLine')),
      );
      if (result.bySubject.isNotEmpty && mounted) {
        await showModalBottomSheet<void>(
          context: context,
          showDragHandle: true,
          builder: (ctx) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text('Ders sonuçları', style: Theme.of(ctx).textTheme.titleMedium),
              const SizedBox(height: 8),
              ...result.bySubject.map(
                (s) => ListTile(
                  title: Text(s.subjectName),
                  subtitle: Text(
                    '${s.correct}D · ${s.wrong}Y · Net ${s.net.toStringAsFixed(2)}',
                  ),
                ),
              ),
            ],
          ),
        );
      }
      if (!mounted) return;
      context.go('/assessment/daily');
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
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
    return Scaffold(
      appBar: AppBar(title: const Text('Optik Form')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null && _session == null
              ? Center(child: Text(_error!))
              : _buildBody(context),
      bottomNavigationBar: _session == null || _session!.questions.isEmpty
          ? null
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: FilledButton(
                  onPressed: _submitting ? null : _submit,
                  child: _submitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Optiği gönder'),
                ),
              ),
            ),
    );
  }

  Widget _buildBody(BuildContext context) {
    final session = _session!;
    if (session.questions.isEmpty) {
      return const Center(child: Text('Sorular henüz hazır değil'));
    }
    final children = <Widget>[
      StudyCard(
        child: Text(
          'PDF’deki cevaplarını buradan işaretle. Boş bırakılan sorular boş sayılır.',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ),
      const SizedBox(height: AppSpacing.md),
    ];
    String? lastSubject;
    for (final q in session.questions) {
      if (q.subjectName != null && q.subjectName != lastSubject) {
        lastSubject = q.subjectName;
        children.add(
          Padding(
            padding: const EdgeInsets.only(top: 8, bottom: 4),
            child: Text(
              q.subjectName!,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
        );
      }
      children.add(
        Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: [
                SizedBox(
                  width: 40,
                  child: Text(
                    '${q.ordIndex + 1}',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
                Expanded(
                  child: Wrap(
                    spacing: 6,
                    children: ['A', 'B', 'C', 'D', 'E'].map((key) {
                      final selected = _answers[q.id] == key;
                      return ChoiceChip(
                        label: Text(key),
                        selected: selected,
                        onSelected: (_) {
                          setState(() {
                            if (selected) {
                              _answers[q.id] = null;
                            } else {
                              _answers[q.id] = key;
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }
    children.add(const SizedBox(height: 80));
    return ListView(padding: AppSpacing.pageWide, children: children);
  }
}
