import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../data/datasources/exam_remote_datasource.dart';
import '../providers/exam_provider.dart';

class EditExamScreen extends ConsumerStatefulWidget {
  const EditExamScreen({super.key, required this.examId});

  final String examId;

  @override
  ConsumerState<EditExamScreen> createState() => _EditExamScreenState();
}

class _EditExamScreenState extends ConsumerState<EditExamScreen> {
  final _title = TextEditingController();
  final _notes = TextEditingController();
  final _duration = TextEditingController();
  String? _examType;
  bool _loading = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final remote = ExamRemoteDatasource(ref.read(dioClientProvider));
      final exam = await remote.getExam(widget.examId);
      _title.text = exam.title;
      _notes.text = exam.notes ?? '';
      _duration.text = exam.durationMinutes.toString();
      _examType = exam.examType;
    } on AppException {
      // leave empty
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  void dispose() {
    _title.dispose();
    _notes.dispose();
    _duration.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final ok = await ref.read(examProvider.notifier).update(widget.examId, {
      'title': _title.text.trim(),
      if (_examType != null) 'exam_type': _examType,
      'notes': _notes.text.trim().isEmpty ? null : _notes.text.trim(),
      'duration_minutes': int.tryParse(_duration.text) ?? 0,
    });
    if (!mounted) return;
    setState(() => _saving = false);
    if (ok) context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final examTypes = profile?.allowedExamTypes ??
        const ['tyt', 'ayt', 'yks', 'lgs', 'kpss', 'ales', 'dgs', 'yds', 'custom'];
    final selected = _examType != null && examTypes.contains(_examType)
        ? _examType
        : (profile?.primaryExamType ?? examTypes.first);

    return Scaffold(
      appBar: AppBar(title: const Text('Deneme Düzenle')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                TextField(
                  controller: _title,
                  decoration: const InputDecoration(labelText: 'Başlık'),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: selected,
                  decoration: const InputDecoration(labelText: 'Sınav tipi'),
                  items: [
                    for (final t in examTypes)
                      DropdownMenuItem(value: t, child: Text(t.toUpperCase())),
                  ],
                  onChanged: (v) => setState(() => _examType = v),
                ),
                TextField(
                  controller: _duration,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Süre (dk)'),
                ),
                TextField(
                  controller: _notes,
                  decoration: const InputDecoration(labelText: 'Notlar'),
                  maxLines: 3,
                ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: _saving ? null : _save,
                  child: const Text('Kaydet'),
                ),
              ],
            ),
    );
  }
}
