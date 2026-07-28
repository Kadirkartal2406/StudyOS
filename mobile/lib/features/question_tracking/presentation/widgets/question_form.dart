import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/question_enums.dart';
import '../providers/topic_picker_provider.dart';

class QuestionFormResult {
  const QuestionFormResult({
    required this.subject,
    required this.questionCount,
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.durationMinutes,
    this.subjectCode,
    this.topic,
    this.topicCode,
    this.difficulty,
    this.source,
    this.examType,
    this.note,
  });

  final String subject;
  final String? subjectCode;
  final String? topic;
  final String? topicCode;
  final int questionCount;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final int durationMinutes;
  final QuestionDifficulty? difficulty;
  final QuestionSource? source;
  final ExamType? examType;
  final String? note;

  Map<String, dynamic> toApiBody() => {
        'subject': subject,
        if (subjectCode != null && subjectCode!.isNotEmpty)
          'subject_code': subjectCode,
        if (topic != null && topic!.isNotEmpty) 'topic': topic,
        if (topicCode != null && topicCode!.isNotEmpty) 'topic_code': topicCode,
        'question_count': questionCount,
        'correct_count': correctCount,
        'wrong_count': wrongCount,
        'blank_count': blankCount,
        'duration_minutes': durationMinutes,
        if (difficulty != null) 'difficulty': difficulty!.apiValue,
        if (source != null) 'source': source!.apiValue,
        if (examType != null) 'exam_type': examType!.apiValue,
        if (note != null && note!.isNotEmpty) 'note': note,
      };
}

/// A simple data class pairing subject name + code.
class SubjectOption {
  const SubjectOption({required this.name, required this.code});
  final String name;
  final String code;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SubjectOption && other.code == code;

  @override
  int get hashCode => code.hashCode;
}

class QuestionForm extends ConsumerStatefulWidget {
  const QuestionForm({
    super.key,
    required this.submitLabel,
    required this.onSubmit,
    this.initial,
    this.allowedExamTypes,
    this.defaultExamType,
    this.subjectOptions = const [],
  });

  final String submitLabel;
  final Future<void> Function(QuestionFormResult result) onSubmit;
  final QuestionFormResult? initial;
  final List<ExamType>? allowedExamTypes;
  final ExamType? defaultExamType;

  /// Subject display names + codes from learning profile.
  final List<SubjectOption> subjectOptions;

  @override
  ConsumerState<QuestionForm> createState() => _QuestionFormState();
}

class _QuestionFormState extends ConsumerState<QuestionForm> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _subject;
  late final TextEditingController _questionCount;
  late final TextEditingController _correct;
  late final TextEditingController _wrong;
  late final TextEditingController _blank;
  late final TextEditingController _duration;
  late final TextEditingController _note;
  QuestionDifficulty? _difficulty;
  QuestionSource? _source;
  ExamType? _examType;
  var _submitting = false;

  SubjectOption? _selectedSubject;
  String? _selectedTopicCode;
  String? _selectedTopicName;

  List<ExamType> get _examChoices {
    final allowed = widget.allowedExamTypes;
    if (allowed == null || allowed.isEmpty) return ExamType.values;
    return allowed;
  }

  @override
  void initState() {
    super.initState();
    final i = widget.initial;
    final subjects = widget.subjectOptions;

    // Try to match initial subject or pick first.
    if (subjects.isNotEmpty) {
      _selectedSubject = subjects.firstWhere(
        (s) => s.name == (i?.subject ?? '') || s.code == (i?.subjectCode ?? ''),
        orElse: () => subjects.first,
      );
    }
    _subject = TextEditingController(
      text: i?.subject ?? (_selectedSubject?.name ?? ''),
    );
    _selectedTopicCode = i?.topicCode;
    _selectedTopicName = i?.topic;

    _questionCount = TextEditingController(text: '${i?.questionCount ?? 20}');
    _correct = TextEditingController(text: '${i?.correctCount ?? 0}');
    _wrong = TextEditingController(text: '${i?.wrongCount ?? 0}');
    _blank = TextEditingController(text: '${i?.blankCount ?? 0}');
    _duration = TextEditingController(text: '${i?.durationMinutes ?? 0}');
    _note = TextEditingController(text: i?.note ?? '');
    _difficulty = i?.difficulty;
    _source = i?.source;
    _examType = i?.examType ?? widget.defaultExamType;
    if (_examType != null && !_examChoices.contains(_examType)) {
      _examType = _examChoices.isNotEmpty ? _examChoices.first : null;
    }
  }

  @override
  void dispose() {
    _subject.dispose();
    _questionCount.dispose();
    _correct.dispose();
    _wrong.dispose();
    _blank.dispose();
    _duration.dispose();
    _note.dispose();
    super.dispose();
  }

  int _intOf(TextEditingController c) => int.tryParse(c.text.trim()) ?? 0;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final q = _intOf(_questionCount);
    final c = _intOf(_correct);
    final w = _intOf(_wrong);
    final b = _intOf(_blank);
    if (c + w + b != q) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
              'Doğru + Yanlış + Boş, toplam soru sayısına eşit olmalı'),
        ),
      );
      return;
    }
    setState(() => _submitting = true);
    try {
      await widget.onSubmit(
        QuestionFormResult(
          subject: _selectedSubject?.name ?? _subject.text.trim(),
          subjectCode: _selectedSubject?.code,
          topic: _selectedTopicName,
          topicCode: _selectedTopicCode,
          questionCount: q,
          correctCount: c,
          wrongCount: w,
          blankCount: b,
          durationMinutes: _intOf(_duration),
          difficulty: _difficulty,
          source: _source,
          examType: _examType,
          note: _note.text.trim().isEmpty ? null : _note.text.trim(),
        ),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Deduplicate by code; match selection by code (not object identity).
    final subjects = <String, SubjectOption>{
      for (final s in widget.subjectOptions)
        if (s.code.isNotEmpty) s.code: s,
    }.values.toList();

    final selectedCode = _selectedSubject?.code;
    final selected = subjects.isEmpty
        ? null
        : subjects.cast<SubjectOption?>().firstWhere(
              (s) => s!.code == selectedCode,
              orElse: () => subjects.first,
            );

    final subjectCode = selected?.code;
    final topicsAsync = subjectCode != null
        ? ref.watch(subjectTopicsProvider(subjectCode))
        : const AsyncValue<List<TopicOption>>.data([]);

    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (subjects.isNotEmpty)
            DropdownButtonFormField<String>(
              value: selected?.code,
              decoration: const InputDecoration(labelText: 'Ders'),
              items: [
                for (final s in subjects)
                  DropdownMenuItem(value: s.code, child: Text(s.name)),
              ],
              onChanged: (code) {
                if (code == null) return;
                final match = subjects.firstWhere((s) => s.code == code);
                setState(() {
                  _selectedSubject = match;
                  _subject.text = match.name;
                  _selectedTopicCode = null;
                  _selectedTopicName = null;
                });
              },
              validator: (v) =>
                  (v == null || v.isEmpty) ? 'Ders zorunlu' : null,
            )
          else
            TextFormField(
              controller: _subject,
              decoration: const InputDecoration(labelText: 'Ders'),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Ders zorunlu' : null,
            ),
          const SizedBox(height: 8),
          _TopicPickerField(
            topicsAsync: topicsAsync,
            selectedCode: _selectedTopicCode,
            onChanged: (code, name) => setState(() {
              _selectedTopicCode = code;
              _selectedTopicName = name;
            }),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _numField(_questionCount, 'Soru')),
              const SizedBox(width: 8),
              Expanded(child: _numField(_correct, 'Doğru')),
            ],
          ),
          Row(
            children: [
              Expanded(child: _numField(_wrong, 'Yanlış')),
              const SizedBox(width: 8),
              Expanded(child: _numField(_blank, 'Boş')),
            ],
          ),
          _numField(_duration, 'Süre (dk)'),
          DropdownButtonFormField<ExamType>(
            value: _examType != null && _examChoices.contains(_examType)
                ? _examType
                : (_examChoices.isNotEmpty ? _examChoices.first : null),
            decoration: const InputDecoration(labelText: 'Sınav Türü'),
            items: [
              for (final e in _examChoices)
                DropdownMenuItem(value: e, child: Text(e.label)),
            ],
            onChanged: (v) => setState(() => _examType = v),
          ),
          // RC2 M22.6 — zorluk / kaynak / not varsayılan olarak gizli (sade form)
          ExpansionTile(
            title: const Text('Ek alanlar'),
            initiallyExpanded: false,
            children: [
              DropdownButtonFormField<QuestionDifficulty>(
                value: _difficulty,
                decoration: const InputDecoration(labelText: 'Zorluk'),
                items: [
                  for (final e in QuestionDifficulty.values)
                    DropdownMenuItem(value: e, child: Text(e.label)),
                ],
                onChanged: (v) => setState(() => _difficulty = v),
              ),
              DropdownButtonFormField<QuestionSource>(
                value: _source,
                decoration: const InputDecoration(labelText: 'Kaynak'),
                items: [
                  for (final e in QuestionSource.values)
                    DropdownMenuItem(value: e, child: Text(e.label)),
                ],
                onChanged: (v) => setState(() => _source = v),
              ),
              TextFormField(
                controller: _note,
                decoration: const InputDecoration(labelText: 'Not'),
                maxLines: 2,
              ),
            ],
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _submitting ? null : _submit,
            child: _submitting
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(widget.submitLabel),
          ),
        ],
      ),
    );
  }

  Widget _numField(TextEditingController c, String label) {
    return TextFormField(
      controller: c,
      decoration: InputDecoration(labelText: label),
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
      validator: (v) {
        if (v == null || v.isEmpty) return 'Zorunlu';
        if (int.tryParse(v) == null) return 'Sayı girin';
        return null;
      },
    );
  }
}

/// Topic picker — shows a dropdown fed from the catalog API.
/// While loading it shows a progress indicator; on error falls back to "—".
class _TopicPickerField extends StatelessWidget {
  const _TopicPickerField({
    required this.topicsAsync,
    required this.selectedCode,
    required this.onChanged,
  });

  final AsyncValue<List<TopicOption>> topicsAsync;
  final String? selectedCode;
  final void Function(String? code, String? name) onChanged;

  @override
  Widget build(BuildContext context) {
    return topicsAsync.when(
      loading: () => InputDecorator(
        decoration: const InputDecoration(labelText: 'Konu'),
        child: const SizedBox(
          height: 20,
          child: LinearProgressIndicator(),
        ),
      ),
      error: (_, __) => const TextField(
        enabled: false,
        decoration: InputDecoration(
          labelText: 'Konu',
          hintText: 'Konu kataloğu yüklenemedi',
        ),
      ),
      data: (topics) {
        if (topics.isEmpty) {
          return const TextField(
            enabled: false,
            decoration: InputDecoration(
              labelText: 'Konu',
              hintText: 'Bu ders için konu bulunamadı',
            ),
          );
        }
        final validCode =
            topics.any((t) => t.code == selectedCode) ? selectedCode : null;
        return DropdownButtonFormField<String>(
          value: validCode,
          decoration: const InputDecoration(labelText: 'Konu'),
          hint: const Text('Seçiniz (isteğe bağlı)'),
          items: [
            for (final t in topics)
              DropdownMenuItem(value: t.code, child: Text(t.name)),
          ],
          onChanged: (code) {
            final topic = topics.firstWhere(
              (t) => t.code == code,
              orElse: () => const TopicOption(code: '', name: ''),
            );
            onChanged(code, topic.name.isEmpty ? null : topic.name);
          },
        );
      },
    );
  }
}
