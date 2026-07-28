import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/exam_remote_datasource.dart';
import '../../domain/entities/exam_entity.dart';
import '../providers/exam_provider.dart';

class ExamDetailScreen extends ConsumerStatefulWidget {
  const ExamDetailScreen({super.key, required this.examId});

  final String examId;

  @override
  ConsumerState<ExamDetailScreen> createState() => _ExamDetailScreenState();
}

class _ExamDetailScreenState extends ConsumerState<ExamDetailScreen> {
  ExamEntity? _exam;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final remote = ExamRemoteDatasource(ref.read(dioClientProvider));
      final model = await remote.getExam(widget.examId);
      setState(() {
        _exam = model.toEntity();
        _loading = false;
      });
    } on AppException catch (e) {
      setState(() {
        _error = e.message;
        _loading = false;
      });
    } catch (_) {
      setState(() {
        _error = 'Deneme yüklenemedi';
        _loading = false;
      });
    }
  }

  Future<void> _delete() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Denemeyi sil'),
        content: const Text('Bu işlem geri alınamaz. Emin misin?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Vazgeç')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Sil')),
        ],
      ),
    );
    if (ok != true) return;
    final deleted = await ref.read(examProvider.notifier).delete(widget.examId);
    if (!mounted) return;
    if (deleted) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final exam = _exam;
    return Scaffold(
      appBar: AppBar(
        title: Text(exam?.title ?? 'Deneme detay'),
        actions: [
          IconButton(
            onPressed: () => context.push('/exams/edit/${widget.examId}'),
            icon: const Icon(Icons.edit_outlined),
          ),
          IconButton(
            onPressed: _delete,
            icon: const Icon(Icons.delete_outline),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : exam == null
                  ? const Center(child: Text('Deneme bulunamadı'))
                  : ListView(
                      padding: const EdgeInsets.all(16),
                      children: [
                        Text(
                          '${exam.examType.toUpperCase()} · '
                          '${DateFormat('dd.MM.yyyy').format(exam.examDate)}',
                        ),
                        Text('Süre: ${exam.durationMinutes} dk'),
                        Text('Toplam net: ${exam.totalNet.toStringAsFixed(2)}'),
                        if (exam.notes != null && exam.notes!.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(exam.notes!),
                          ),
                        const SizedBox(height: 16),
                        Text('Ders sonuçları', style: Theme.of(context).textTheme.titleLarge),
                        const SizedBox(height: 8),
                        for (final r in exam.results)
                          Card(
                            child: ListTile(
                              title: Text(r.subject),
                              subtitle: Text(
                                'D ${r.correctCount} · Y ${r.wrongCount} · B ${r.blankCount}',
                              ),
                              trailing: Text('Net ${r.netScore.toStringAsFixed(1)}'),
                            ),
                          ),
                      ],
                    ),
    );
  }
}
