import 'package:flutter/material.dart';

import '../../../../core/errors/app_exception.dart';
import '../../domain/entities/study_time.dart';

/// Add/Edit Study Plan ekranları arasında paylaşılan form gövdesi.
/// Yalnızca UI + client-side doğrulama içerir; kaydetme işlemi çağıran
/// ekranın sağladığı [onSubmit] callback'i üzerinden yapılır.
class StudyPlanFormResult {
  const StudyPlanFormResult({
    required this.title,
    required this.subject,
    this.topic,
    required this.targetQuestionCount,
    required this.estimatedMinutes,
    this.plannedStartTime,
    this.plannedEndTime,
  });

  final String title;
  final String subject;
  final String? topic;
  final int targetQuestionCount;
  final int estimatedMinutes;
  final StudyTime? plannedStartTime;
  final StudyTime? plannedEndTime;
}

class StudyPlanForm extends StatefulWidget {
  const StudyPlanForm({
    super.key,
    required this.onSubmit,
    required this.submitLabel,
    this.initialTitle,
    this.initialSubject,
    this.initialTopic,
    this.initialTargetQuestionCount,
    this.initialEstimatedMinutes,
    this.initialStartTime,
    this.initialEndTime,
  });

  final Future<void> Function(StudyPlanFormResult result) onSubmit;
  final String submitLabel;
  final String? initialTitle;
  final String? initialSubject;
  final String? initialTopic;
  final int? initialTargetQuestionCount;
  final int? initialEstimatedMinutes;
  final StudyTime? initialStartTime;
  final StudyTime? initialEndTime;

  @override
  State<StudyPlanForm> createState() => _StudyPlanFormState();
}

class _StudyPlanFormState extends State<StudyPlanForm> {
  final _formKey = GlobalKey<FormState>();
  late final _titleController =
      TextEditingController(text: widget.initialTitle);
  late final _subjectController =
      TextEditingController(text: widget.initialSubject);
  late final _topicController =
      TextEditingController(text: widget.initialTopic);
  late final _questionCountController = TextEditingController(
    text: widget.initialTargetQuestionCount?.toString(),
  );
  late final _minutesController =
      TextEditingController(text: widget.initialEstimatedMinutes?.toString());

  StudyTime? _startTime;
  StudyTime? _endTime;
  bool _useTimeRange = false;
  bool _isSubmitting = false;
  String? _submitError;

  @override
  void initState() {
    super.initState();
    _startTime = widget.initialStartTime;
    _endTime = widget.initialEndTime;
    _useTimeRange = _startTime != null && _endTime != null;
  }

  @override
  void dispose() {
    _titleController.dispose();
    _subjectController.dispose();
    _topicController.dispose();
    _questionCountController.dispose();
    _minutesController.dispose();
    super.dispose();
  }

  Future<void> _pickTime({required bool isStart}) async {
    final initial = (isStart ? _startTime : _endTime) ??
        const StudyTime(hour: 9, minute: 0);
    final picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: initial.hour, minute: initial.minute),
    );
    if (picked == null) return;
    setState(() {
      final time = StudyTime(hour: picked.hour, minute: picked.minute);
      if (isStart) {
        _startTime = time;
      } else {
        _endTime = time;
      }
    });
  }

  Future<void> _submit() async {
    setState(() => _submitError = null);
    if (!_formKey.currentState!.validate()) return;

    if (_useTimeRange) {
      if (_startTime == null || _endTime == null) {
        setState(() {
          _submitError = 'Başlangıç ve bitiş saati birlikte seçilmeli';
        });
        return;
      }
      if (_endTime!.totalMinutes <= _startTime!.totalMinutes) {
        setState(() {
          _submitError = 'Bitiş saati başlangıçtan büyük olmalıdır';
        });
        return;
      }
    }

    setState(() => _isSubmitting = true);
    try {
      await widget.onSubmit(
        StudyPlanFormResult(
          title: _titleController.text.trim(),
          subject: _subjectController.text.trim(),
          topic: _topicController.text.trim().isEmpty
              ? null
              : _topicController.text.trim(),
          targetQuestionCount: int.parse(_questionCountController.text),
          estimatedMinutes: int.parse(_minutesController.text),
          plannedStartTime: _useTimeRange ? _startTime : null,
          plannedEndTime: _useTimeRange ? _endTime : null,
        ),
      );
    } catch (e) {
      if (mounted) {
        final message =
            e is AppException ? e.message : 'Beklenmeyen bir hata oluştu';
        setState(() => _submitError = message);
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          TextFormField(
            controller: _titleController,
            decoration: const InputDecoration(labelText: 'Başlık *'),
            textInputAction: TextInputAction.next,
            validator: (value) => (value == null || value.trim().isEmpty)
                ? 'Başlık boş olamaz'
                : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _subjectController,
            decoration: const InputDecoration(labelText: 'Ders *'),
            textInputAction: TextInputAction.next,
            validator: (value) => (value == null || value.trim().isEmpty)
                ? 'Ders boş olamaz'
                : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _topicController,
            decoration: const InputDecoration(labelText: 'Konu (opsiyonel)'),
            textInputAction: TextInputAction.next,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: _questionCountController,
                  decoration:
                      const InputDecoration(labelText: 'Hedef Soru Sayısı *'),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    final parsed = int.tryParse(value ?? '');
                    if (parsed == null || parsed <= 0) return 'Soru > 0 olmalı';
                    return null;
                  },
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextFormField(
                  controller: _minutesController,
                  decoration:
                      const InputDecoration(labelText: 'Tahmini Süre (dk) *'),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    final parsed = int.tryParse(value ?? '');
                    if (parsed == null || parsed <= 0) {
                      return 'Dakika > 0 olmalı';
                    }
                    return null;
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Saat aralığı belirle'),
            value: _useTimeRange,
            onChanged: (value) => setState(() => _useTimeRange = value),
          ),
          if (_useTimeRange)
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickTime(isStart: true),
                    icon: const Icon(Icons.schedule_rounded, size: 18),
                    label: Text(_startTime?.label ?? 'Başlangıç'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _pickTime(isStart: false),
                    icon: const Icon(Icons.schedule_rounded, size: 18),
                    label: Text(_endTime?.label ?? 'Bitiş'),
                  ),
                ),
              ],
            ),
          if (_submitError != null) ...[
            const SizedBox(height: 12),
            Text(
              _submitError!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ],
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _isSubmitting ? null : _submit,
            child: _isSubmitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(widget.submitLabel),
          ),
        ],
      ),
    );
  }
}
