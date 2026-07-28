import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../providers/exam_provider.dart';
import '../providers/exam_state.dart';

class _ResultDraft {
  _ResultDraft({String? subject}) {
    if (subject != null) this.subject.text = subject;
  }

  final subject = TextEditingController();
  final correct = TextEditingController(text: '0');
  final wrong = TextEditingController(text: '0');
  final blank = TextEditingController(text: '0');
  final duration = TextEditingController(text: '0');

  void dispose() {
    subject.dispose();
    correct.dispose();
    wrong.dispose();
    blank.dispose();
    duration.dispose();
  }

  Map<String, dynamic>? toJson() {
    final s = subject.text.trim();
    if (s.isEmpty) return null;
    final c = int.tryParse(correct.text) ?? 0;
    final w = int.tryParse(wrong.text) ?? 0;
    final b = int.tryParse(blank.text) ?? 0;
    final total = c + w + b;
    if (total < 1) return null;
    return {
      'subject': s,
      'correct_count': c,
      'wrong_count': w,
      'blank_count': b,
      'question_count': total,
      'duration_minutes': int.tryParse(duration.text) ?? 0,
    };
  }
}

class AddExamScreen extends ConsumerStatefulWidget {
  const AddExamScreen({super.key});

  @override
  ConsumerState<AddExamScreen> createState() => _AddExamScreenState();
}

class _AddExamScreenState extends ConsumerState<AddExamScreen> {
  static const _fallbackExamTypes = [
    'tyt',
    'ayt',
    'yks',
    'lgs',
    'kpss',
    'ales',
    'dgs',
    'yds',
    'custom',
  ];

  final _title = TextEditingController();
  final _notes = TextEditingController();
  final _duration = TextEditingController(text: '120');
  /// Always kept in sync with the dropdown (never rely on display-only fallback).
  String _type = 'tyt';
  DateTime _date = DateTime.now();
  final _results = <_ResultDraft>[_ResultDraft()];
  bool _saving = false;
  bool _defaultsApplied = false;

  @override
  void dispose() {
    _title.dispose();
    _notes.dispose();
    _duration.dispose();
    for (final r in _results) {
      r.dispose();
    }
    super.dispose();
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _date,
      firstDate: DateTime(2020),
      lastDate: DateTime(2035),
    );
    if (picked != null) setState(() => _date = picked);
  }

  Future<void> _save() async {
    final title = _title.text.trim();
    if (title.isEmpty) {
      _showMessage('Başlık gerekli');
      return;
    }
    final profile = ref.read(learningProfileProvider).valueOrNull;
    final examTypes = (profile?.allowedExamTypes.isNotEmpty ?? false)
        ? profile!.allowedExamTypes
        : _fallbackExamTypes;
    final examType = examTypes.contains(_type) ? _type : examTypes.first;
    if (_type != examType) {
      setState(() => _type = examType);
    }
    final results = <Map<String, dynamic>>[];
    for (final r in _results) {
      final j = r.toJson();
      if (j != null) results.add(j);
    }
    setState(() => _saving = true);
    final ok = await ref.read(examProvider.notifier).create({
      'title': title,
      'exam_type': examType,
      'exam_date': DateFormat('yyyy-MM-dd').format(_date),
      'duration_minutes': int.tryParse(_duration.text) ?? 0,
      'notes': _notes.text.trim().isEmpty ? null : _notes.text.trim(),
      'results': results,
    });
    if (!mounted) return;
    setState(() => _saving = false);
    if (ok) {
      context.pop();
    } else {
      final state = ref.read(examProvider);
      final msg = state is ExamLoaded ? state.errorMessage : null;
      _showMessage(msg ?? 'Deneme kaydedilemedi');
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(learningProfileProvider);
    final profile = profileAsync.valueOrNull;
    final examTypes = (profile?.allowedExamTypes.isNotEmpty ?? false)
        ? profile!.allowedExamTypes
        : _fallbackExamTypes;
    final subjects = profile?.subjectNames ?? const <String>[];

    // Apply profile defaults once loading settles (or immediately on fallback).
    if (!_defaultsApplied && !profileAsync.isLoading) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted || _defaultsApplied) return;
        setState(() {
          final preferred =
              profile?.activeExamType ?? profile?.primaryExamType;
          if (preferred != null && examTypes.contains(preferred)) {
            _type = preferred;
          } else if (!examTypes.contains(_type)) {
            _type = examTypes.first;
          }
          if (_results.length == 1 &&
              _results.first.subject.text.isEmpty &&
              subjects.isNotEmpty) {
            _results.first.subject.text = subjects.first;
          }
          _defaultsApplied = true;
        });
      });
    }

    final selectedType =
        examTypes.contains(_type) ? _type : examTypes.first;

    return Scaffold(
      appBar: AppBar(title: const Text('Deneme Ekle')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _title,
            decoration: const InputDecoration(labelText: 'Başlık'),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: selectedType,
            decoration: const InputDecoration(labelText: 'Sınav tipi'),
            items: [
              for (final t in examTypes)
                DropdownMenuItem(value: t, child: Text(t.toUpperCase())),
            ],
            onChanged: (v) {
              if (v != null) setState(() => _type = v);
            },
          ),
          const SizedBox(height: 12),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: Text('Tarih: ${DateFormat('dd.MM.yyyy').format(_date)}'),
            trailing: const Icon(Icons.calendar_today),
            onTap: _pickDate,
          ),
          TextField(
            controller: _duration,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Süre (dk)'),
          ),
          TextField(
            controller: _notes,
            decoration: const InputDecoration(labelText: 'Notlar'),
            maxLines: 2,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Text('Ders sonuçları', style: Theme.of(context).textTheme.titleMedium),
              const Spacer(),
              TextButton.icon(
                onPressed: () => setState(() => _results.add(_ResultDraft())),
                icon: const Icon(Icons.add),
                label: const Text('Ders'),
              ),
            ],
          ),
          for (var i = 0; i < _results.length; i++)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  children: [
                    if (subjects.isNotEmpty)
                      DropdownButtonFormField<String>(
                        value: subjects.contains(_results[i].subject.text)
                            ? _results[i].subject.text
                            : null,
                        decoration: const InputDecoration(labelText: 'Ders'),
                        items: [
                          for (final s in subjects)
                            DropdownMenuItem(value: s, child: Text(s)),
                        ],
                        onChanged: (v) {
                          if (v != null) {
                            setState(() => _results[i].subject.text = v);
                          }
                        },
                      )
                    else
                      TextField(
                        controller: _results[i].subject,
                        decoration: const InputDecoration(labelText: 'Ders'),
                      ),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _results[i].correct,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(labelText: 'D'),
                          ),
                        ),
                        Expanded(
                          child: TextField(
                            controller: _results[i].wrong,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(labelText: 'Y'),
                          ),
                        ),
                        Expanded(
                          child: TextField(
                            controller: _results[i].blank,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(labelText: 'B'),
                          ),
                        ),
                      ],
                    ),
                    if (_results.length > 1)
                      Align(
                        alignment: Alignment.centerRight,
                        child: IconButton(
                          onPressed: () => setState(() {
                            _results[i].dispose();
                            _results.removeAt(i);
                          }),
                          icon: const Icon(Icons.delete_outline),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _saving ? null : _save,
            child: _saving
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Kaydet'),
          ),
        ],
      ),
    );
  }
}
