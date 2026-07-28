import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

import '../../domain/entities/goal_entity.dart';
import '../../domain/entities/product_goal_type.dart';

class GoalFormResult {
  const GoalFormResult({
    required this.title,
    required this.targetValue,
    required this.priority,
    required this.startDate,
    required this.endDate,
    this.productGoalType,
    this.goalType,
    this.period,
    this.description,
    this.subject,
    this.topic,
    this.examType,
    this.status,
  });

  final String title;
  final String? description;
  final ProductGoalType? productGoalType;
  final GoalType? goalType;
  final double targetValue;
  final GoalPriority priority;
  final GoalPeriod? period;
  final String? subject;
  final String? topic;
  final String? examType;
  final DateTime startDate;
  final DateTime endDate;
  final GoalStatus? status;

  Map<String, dynamic> toCreateBody() {
    final fmt = DateFormat('yyyy-MM-dd');
    if (productGoalType != null) {
      return {
        'title': title,
        if (description != null && description!.isNotEmpty)
          'description': description,
        'product_goal_type': productGoalType!.apiValue,
        'target_value': targetValue,
        'priority': priority.apiValue,
        if (subject != null && subject!.isNotEmpty) 'subject': subject,
        if (topic != null && topic!.isNotEmpty) 'topic': topic,
        if (examType != null && examType!.isNotEmpty) 'exam_type': examType,
        'start_date': fmt.format(startDate),
        'end_date': fmt.format(endDate),
      };
    }
    return {
      'title': title,
      if (description != null && description!.isNotEmpty)
        'description': description,
      'goal_type': (goalType ?? GoalType.custom).apiValue,
      'target_value': targetValue,
      'priority': priority.apiValue,
      'period': (period ?? GoalPeriod.weekly).apiValue,
      if (subject != null && subject!.isNotEmpty) 'subject': subject,
      if (topic != null && topic!.isNotEmpty) 'topic': topic,
      if (examType != null && examType!.isNotEmpty) 'exam_type': examType,
      'start_date': fmt.format(startDate),
      'end_date': fmt.format(endDate),
    };
  }

  Map<String, dynamic> toUpdateBody() {
    final fmt = DateFormat('yyyy-MM-dd');
    return {
      'title': title,
      if (description != null) 'description': description,
      'target_value': targetValue,
      'priority': priority.apiValue,
      if (status != null) 'status': status!.apiValue,
      if (subject != null) 'subject': subject,
      if (topic != null) 'topic': topic,
      if (examType != null) 'exam_type': examType,
      'start_date': fmt.format(startDate),
      'end_date': fmt.format(endDate),
    };
  }
}

class GoalForm extends StatefulWidget {
  const GoalForm({
    super.key,
    required this.submitLabel,
    required this.onSubmit,
    this.initial,
    this.allowStatusEdit = false,
    this.allowedExamTypes,
    this.defaultExamType,
    this.subjectOptions = const [],
  });

  final String submitLabel;
  final Future<void> Function(GoalFormResult result) onSubmit;
  final GoalFormResult? initial;
  final bool allowStatusEdit;
  final List<String>? allowedExamTypes;
  final String? defaultExamType;
  final List<String> subjectOptions;

  @override
  State<GoalForm> createState() => _GoalFormState();
}

class _GoalFormState extends State<GoalForm> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _title;
  late final TextEditingController _description;
  late final TextEditingController _target;
  late final TextEditingController _subject;
  late final TextEditingController _topic;
  late ProductGoalType _productType;
  late GoalPriority _priority;
  late DateTime _startDate;
  late DateTime _endDate;
  GoalStatus? _status;
  String? _examType;
  var _submitting = false;

  List<String> get _examChoices {
    final allowed = widget.allowedExamTypes;
    if (allowed == null || allowed.isEmpty) {
      return const ['tyt', 'ayt', 'yks', 'lgs', 'kpss'];
    }
    return allowed;
  }

  ProductGoalType? _inferProduct(GoalType? type) {
    if (type == null) return null;
    return switch (type) {
      GoalType.studyTime => ProductGoalType.dailyStudyTime,
      GoalType.question => ProductGoalType.weeklyQuestions,
      GoalType.pomodoro => ProductGoalType.dailyStudyTime,
      GoalType.subject => ProductGoalType.branchNet,
      GoalType.topic => ProductGoalType.weeklyQuestions,
      GoalType.custom => ProductGoalType.netTarget,
    };
  }

  @override
  void initState() {
    super.initState();
    final i = widget.initial;
    final now = DateTime.now();
    _title = TextEditingController(text: i?.title ?? '');
    _description = TextEditingController(text: i?.description ?? '');
    _target = TextEditingController(
      text: i != null ? i.targetValue.toStringAsFixed(0) : '60',
    );
    final subjects = widget.subjectOptions;
    _subject = TextEditingController(
      text: i?.subject ?? (subjects.isNotEmpty ? subjects.first : ''),
    );
    _topic = TextEditingController(text: i?.topic ?? '');
    _productType = i?.productGoalType ??
        _inferProduct(i?.goalType) ??
        ProductGoalType.dailyStudyTime;
    _priority = i?.priority ?? GoalPriority.medium;
    _startDate = i?.startDate ?? DateTime(now.year, now.month, now.day);
    _endDate = i?.endDate ??
        DateTime(now.year, now.month, now.day).add(const Duration(days: 7));
    _status = i?.status ?? GoalStatus.active;
    _examType = i?.examType ?? widget.defaultExamType ?? _examChoices.first;
    if (_examType != null && !_examChoices.contains(_examType)) {
      _examType = _examChoices.first;
    }
  }

  @override
  void dispose() {
    _title.dispose();
    _description.dispose();
    _target.dispose();
    _subject.dispose();
    _topic.dispose();
    super.dispose();
  }

  Future<void> _pickDate({required bool isStart}) async {
    final initial = isStart ? _startDate : _endDate;
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (picked == null) return;
    setState(() {
      if (isStart) {
        _startDate = picked;
        if (_endDate.isBefore(_startDate)) _endDate = _startDate;
      } else {
        _endDate = picked;
      }
    });
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_productType.requiresSubject && _subject.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bu hedef tipi için ders zorunlu')),
      );
      return;
    }
    setState(() => _submitting = true);
    try {
      await widget.onSubmit(
        GoalFormResult(
          title: _title.text.trim(),
          description: _description.text.trim().isEmpty
              ? null
              : _description.text.trim(),
          productGoalType: widget.initial?.productGoalType != null ||
                  widget.initial == null
              ? _productType
              : widget.initial?.productGoalType,
          goalType: widget.initial?.goalType,
          targetValue: double.tryParse(_target.text.trim()) ?? 0,
          priority: _priority,
          period: widget.initial?.period,
          subject: _subject.text.trim().isEmpty ? null : _subject.text.trim(),
          topic: _topic.text.trim().isEmpty ? null : _topic.text.trim(),
          examType: _examType,
          startDate: _startDate,
          endDate: _endDate,
          status: widget.allowStatusEdit ? _status : null,
        ),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd.MM.yyyy');
    final showSubject = _productType.showSubject;
    final isCreate = widget.initial == null;

    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextFormField(
            controller: _title,
            decoration: const InputDecoration(
              labelText: 'Başlık',
              border: OutlineInputBorder(),
            ),
            validator: (v) =>
                (v == null || v.trim().isEmpty) ? 'Başlık zorunlu' : null,
          ),
          const SizedBox(height: 12),
          TextFormField(
            controller: _description,
            decoration: const InputDecoration(
              labelText: 'Açıklama (opsiyonel)',
              border: OutlineInputBorder(),
            ),
            maxLines: 2,
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<ProductGoalType>(
            value: _productType,
            decoration: const InputDecoration(
              labelText: 'Hedef tipi',
              border: OutlineInputBorder(),
            ),
            items: ProductGoalType.values
                .map(
                  (e) => DropdownMenuItem(value: e, child: Text(e.label)),
                )
                .toList(),
            onChanged: isCreate
                ? (v) {
                    if (v != null) setState(() => _productType = v);
                  }
                : null,
          ),
          const SizedBox(height: 12),
          TextFormField(
            controller: _target,
            decoration: InputDecoration(
              labelText: _productType.targetLabel,
              border: const OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
            inputFormatters: [FilteringTextInputFormatter.digitsOnly],
            validator: (v) {
              final n = double.tryParse(v ?? '');
              if (n == null || n <= 0) return 'Pozitif bir değer girin';
              return null;
            },
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<GoalPriority>(
            value: _priority,
            decoration: const InputDecoration(
              labelText: 'Öncelik',
              border: OutlineInputBorder(),
            ),
            items: GoalPriority.values
                .map(
                  (e) => DropdownMenuItem(value: e, child: Text(e.label)),
                )
                .toList(),
            onChanged: (v) {
              if (v != null) setState(() => _priority = v);
            },
          ),
          if (widget.allowStatusEdit) ...[
            const SizedBox(height: 12),
            DropdownButtonFormField<GoalStatus>(
              value: _status,
              decoration: const InputDecoration(
                labelText: 'Durum',
                border: OutlineInputBorder(),
              ),
              items: GoalStatus.values
                  .map(
                    (e) => DropdownMenuItem(value: e, child: Text(e.label)),
                  )
                  .toList(),
              onChanged: (v) {
                if (v != null) setState(() => _status = v);
              },
            ),
          ],
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _examType != null && _examChoices.contains(_examType)
                ? _examType
                : _examChoices.first,
            decoration: const InputDecoration(
              labelText: 'Sınav (Primary Exam)',
              border: OutlineInputBorder(),
              helperText: 'Profilindeki sınavlardan seçilir',
            ),
            items: [
              for (final t in _examChoices)
                DropdownMenuItem(value: t, child: Text(t.toUpperCase())),
            ],
            onChanged: (v) => setState(() => _examType = v),
          ),
          if (showSubject) ...[
            const SizedBox(height: 12),
            if (widget.subjectOptions.isNotEmpty)
              DropdownButtonFormField<String>(
                value: widget.subjectOptions.contains(_subject.text)
                    ? _subject.text
                    : widget.subjectOptions.first,
                decoration: const InputDecoration(
                  labelText: 'Ders',
                  border: OutlineInputBorder(),
                ),
                items: [
                  for (final s in widget.subjectOptions)
                    DropdownMenuItem(value: s, child: Text(s)),
                ],
                onChanged: (v) {
                  if (v != null) setState(() => _subject.text = v);
                },
              )
            else
              TextFormField(
                controller: _subject,
                decoration: const InputDecoration(
                  labelText: 'Ders',
                  border: OutlineInputBorder(),
                ),
              ),
          ],
          const SizedBox(height: 12),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Başlangıç'),
            subtitle: Text(fmt.format(_startDate)),
            trailing: const Icon(Icons.calendar_today_outlined),
            onTap: () => _pickDate(isStart: true),
          ),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Bitiş'),
            subtitle: Text(fmt.format(_endDate)),
            trailing: const Icon(Icons.event_outlined),
            onTap: () => _pickDate(isStart: false),
          ),
          const SizedBox(height: 20),
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
}
