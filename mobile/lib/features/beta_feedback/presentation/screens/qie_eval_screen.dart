import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_spacing.dart';

/// Sprint 25 — thin teacher/human evaluation UI for QIE questions.
class QieEvalScreen extends ConsumerStatefulWidget {
  const QieEvalScreen({super.key});

  @override
  ConsumerState<QieEvalScreen> createState() => _QieEvalScreenState();
}

class _QieEvalScreenState extends ConsumerState<QieEvalScreen> {
  List<Map<String, dynamic>> _queue = [];
  int _index = 0;
  bool _loading = true;
  bool _sending = false;
  String? _error;

  int _examFeel = 3;
  int _language = 3;
  int _difficulty = 3;
  int _optionQuality = 3;
  int _objectiveFit = 3;
  int _overall = 3;
  final _notes = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _notes.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final dio = ref.read(dioClientProvider);
      final res = await dio.get<Map<String, dynamic>>(ApiEndpoints.qieEvalQueue);
      final data = res.data?['data'];
      final list = (data is List)
          ? data.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
          : <Map<String, dynamic>>[];
      setState(() {
        _queue = list;
        _index = 0;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _loading = false;
        _error = 'Kuyruk yüklenemedi';
      });
    }
  }

  Future<void> _submit() async {
    if (_queue.isEmpty || _index >= _queue.length) return;
    final item = _queue[_index];
    setState(() => _sending = true);
    try {
      final dio = ref.read(dioClientProvider);
      await dio.post<Map<String, dynamic>>(
        ApiEndpoints.qieEvalSubmit,
        data: {
          'question_ref_type': item['question_ref_type'],
          'question_ref_id': item['question_ref_id'],
          'exam_feel': _examFeel,
          'language': _language,
          'difficulty': _difficulty,
          'option_quality': _optionQuality,
          'objective_fit': _objectiveFit,
          'overall': _overall,
          if (_notes.text.trim().isNotEmpty) 'notes': _notes.text.trim(),
          'stem_preview': item['stem_preview'],
        },
      );
      if (!mounted) return;
      setState(() {
        _sending = false;
        _index += 1;
        _notes.clear();
        _examFeel = _language = _difficulty = _optionQuality =
            _objectiveFit = _overall = 3;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _sending = false;
        _error = 'Kayıt başarısız';
      });
    }
  }

  Widget _slider(String label, int value, ValueChanged<int> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$label: $value'),
        Slider(
          value: value.toDouble(),
          min: 1,
          max: 5,
          divisions: 4,
          label: '$value',
          onChanged: (v) => onChanged(v.round()),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Soru değerlendirme')),
      body: SafeArea(
        child: Padding(
          padding: AppSpacing.pageWide,
          child: _loading
              ? const Center(child: CircularProgressIndicator())
              : _error != null && _queue.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(_error!),
                          TextButton(onPressed: _load, child: const Text('Yenile')),
                        ],
                      ),
                    )
                  : _index >= _queue.length
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Text('Kuyruk bitti.'),
                              TextButton(onPressed: _load, child: const Text('Yenile')),
                            ],
                          ),
                        )
                      : ListView(
                          children: [
                            Text(
                              'Soru ${_index + 1}/${_queue.length}',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              (_queue[_index]['stem_preview'] as String?) ?? '',
                              style: Theme.of(context).textTheme.bodyLarge,
                            ),
                            const SizedBox(height: 16),
                            _slider('Gerçek sınav hissi', _examFeel,
                                (v) => setState(() => _examFeel = v)),
                            _slider('Dil', _language,
                                (v) => setState(() => _language = v)),
                            _slider('Zorluk', _difficulty,
                                (v) => setState(() => _difficulty = v)),
                            _slider('Seçenek kalitesi', _optionQuality,
                                (v) => setState(() => _optionQuality = v)),
                            _slider('Kazanım uyumu', _objectiveFit,
                                (v) => setState(() => _objectiveFit = v)),
                            _slider('Genel kalite', _overall,
                                (v) => setState(() => _overall = v)),
                            TextField(
                              controller: _notes,
                              decoration: const InputDecoration(
                                labelText: 'Not (opsiyonel)',
                              ),
                              maxLines: 2,
                            ),
                            if (_error != null) ...[
                              const SizedBox(height: 8),
                              Text(_error!,
                                  style: TextStyle(
                                      color: Theme.of(context).colorScheme.error)),
                            ],
                            const SizedBox(height: 16),
                            FilledButton(
                              onPressed: _sending ? null : _submit,
                              child: Text(_sending ? 'Kaydediliyor…' : 'Kaydet ve sonraki'),
                            ),
                          ],
                        ),
        ),
      ),
    );
  }
}
