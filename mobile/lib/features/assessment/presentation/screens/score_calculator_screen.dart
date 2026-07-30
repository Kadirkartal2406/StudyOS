import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_spacing.dart';

/// Sprint 33 / 35 — Sınava Özel Ders Bazlı ÖSYM Tahmini Puan Hesaplama (hesaplama.net standartlarında)
class ScoreCalculatorScreen extends ConsumerStatefulWidget {
  const ScoreCalculatorScreen({super.key});

  @override
  ConsumerState<ScoreCalculatorScreen> createState() => _ScoreCalculatorScreenState();
}

class _ScoreCalculatorScreenState extends ConsumerState<ScoreCalculatorScreen> {
  String _selectedExam = 'KPSS';

  final Map<String, Map<String, TextEditingController>> _examControllers = {
    'KPSS': {
      'Türkçe (30 Soru)': TextEditingController(text: '24'),
      'Matematik (30 Soru)': TextEditingController(text: '20'),
      'Tarih (27 Soru)': TextEditingController(text: '18'),
      'Coğrafya (18 Soru)': TextEditingController(text: '12'),
      'Vatandaşlık & Güncel (15 Soru)': TextEditingController(text: '10'),
    },
    'TYT': {
      'Türkçe (40 Soru)': TextEditingController(text: '32'),
      'Temel Matematik (40 Soru)': TextEditingController(text: '28'),
      'Sosyal Bilimler (20 Soru)': TextEditingController(text: '15'),
      'Fen Bilimleri (20 Soru)': TextEditingController(text: '14'),
    },
    'AYT': {
      'Matematik (40 Soru)': TextEditingController(text: '30'),
      'Fen Bilimleri (40 Soru)': TextEditingController(text: '25'),
      'Türk Dili ve Ed. - Sos 1 (40 Soru)': TextEditingController(text: '28'),
      'Sosyal Bilimler 2 (40 Soru)': TextEditingController(text: '24'),
    },
    'LGS': {
      'Türkçe (20 Soru)': TextEditingController(text: '16'),
      'Matematik (20 Soru)': TextEditingController(text: '14'),
      'Fen Bilimleri (20 Soru)': TextEditingController(text: '15'),
      'T.C. İnkılap (10 Soru)': TextEditingController(text: '8'),
      'Din Kültürü (10 Soru)': TextEditingController(text: '9'),
      'İngilizce (10 Soru)': TextEditingController(text: '8'),
    },
  };

  final Map<String, Map<String, TextEditingController>> _examWrongControllers = {
    'KPSS': {
      'Türkçe (30 Soru)': TextEditingController(text: '4'),
      'Matematik (30 Soru)': TextEditingController(text: '5'),
      'Tarih (27 Soru)': TextEditingController(text: '3'),
      'Coğrafya (18 Soru)': TextEditingController(text: '2'),
      'Vatandaşlık & Güncel (15 Soru)': TextEditingController(text: '2'),
    },
    'TYT': {
      'Türkçe (40 Soru)': TextEditingController(text: '5'),
      'Temel Matematik (40 Soru)': TextEditingController(text: '4'),
      'Sosyal Bilimler (20 Soru)': TextEditingController(text: '3'),
      'Fen Bilimleri (20 Soru)': TextEditingController(text: '3'),
    },
    'AYT': {
      'Matematik (40 Soru)': TextEditingController(text: '6'),
      'Fen Bilimleri (40 Soru)': TextEditingController(text: '5'),
      'Türk Dili ve Ed. - Sos 1 (40 Soru)': TextEditingController(text: '4'),
      'Sosyal Bilimler 2 (40 Soru)': TextEditingController(text: '4'),
    },
    'LGS': {
      'Türkçe (20 Soru)': TextEditingController(text: '3'),
      'Matematik (20 Soru)': TextEditingController(text: '3'),
      'Fen Bilimleri (20 Soru)': TextEditingController(text: '3'),
      'T.C. İnkılap (10 Soru)': TextEditingController(text: '1'),
      'Din Kültürü (10 Soru)': TextEditingController(text: '1'),
      'İngilizce (10 Soru)': TextEditingController(text: '1'),
    },
  };

  double? _calculatedScore;
  double _totalNet = 0.0;
  String _badge = '🥈 Altın Hedef';

  void _calculate() {
    double netSum = 0;
    final penalty = _selectedExam == 'LGS' ? 3.0 : 4.0;

    final corrects = _examControllers[_selectedExam]!;
    final wrongs = _examWrongControllers[_selectedExam]!;

    corrects.forEach((subject, cController) {
      final wController = wrongs[subject];
      final correct = int.tryParse(cController.text) ?? 0;
      final wrong = int.tryParse(wController?.text ?? '0') ?? 0;
      final net = (correct - (wrong / penalty)).clamp(0.0, 100.0);
      netSum += net;
    });

    double score = 0;
    final maxScore = _selectedExam == 'KPSS' ? 100.0 : 500.0;

    if (_selectedExam == 'KPSS') {
      score = (40.0 + (netSum * 0.50)).clamp(40.0, 100.0);
    } else if (_selectedExam == 'TYT') {
      score = (100.0 + (netSum * 3.33)).clamp(100.0, 500.0);
    } else if (_selectedExam == 'AYT') {
      score = (100.0 + (netSum * 2.50)).clamp(100.0, 500.0);
    } else {
      score = (100.0 + (netSum * 4.44)).clamp(100.0, 500.0);
    }

    setState(() {
      _totalNet = double.parse(netSum.toStringAsFixed(2));
      _calculatedScore = double.parse(score.toStringAsFixed(2));
      final pct = (score / maxScore) * 100.0;
      if (pct >= 90) {
        _badge = '🥇 Derece Adayı (Şampiyon)';
      } else if (pct >= 75) {
        _badge = '🥈 Altın Hedef';
      } else if (pct >= 50) {
        _badge = '🥉 Gümüş İlerleme';
      } else {
        _badge = '🌱 Başlangıç Seviyesi';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final subjectCorrects = _examControllers[_selectedExam]!;
    final subjectWrongs = _examWrongControllers[_selectedExam]!;

    return Scaffold(
      appBar: AppBar(
        title: Text('$_selectedExam Tahmini Puan Hesaplama'),
      ),
      body: SafeArea(
        child: ListView(
          padding: AppSpacing.pageWide,
          children: [
            // Disclaimer Alert Banner
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: scheme.primaryContainer.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: scheme.primary.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline_rounded, color: scheme.primary),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Hesaplanan değer ÖSYM ve MEB katsayıları (hesaplama.net standartlarında) temel alınarak hesaplanmış Tahmini Puan\'dır.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: scheme.onSurfaceVariant,
                          ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Exam Selector
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'KPSS', label: Text('KPSS')),
                ButtonSegment(value: 'TYT', label: Text('TYT')),
                ButtonSegment(value: 'AYT', label: Text('AYT')),
                ButtonSegment(value: 'LGS', label: Text('LGS')),
              ],
              selected: {_selectedExam},
              onSelectionChanged: (val) {
                setState(() {
                  _selectedExam = val.first;
                  _calculatedScore = null;
                });
              },
            ),
            const SizedBox(height: 20),

            // Inputs Table for Selected Exam
            ...subjectCorrects.keys.map((subject) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Row(
                  children: [
                    Expanded(
                      flex: 4,
                      child: Text(
                        subject,
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ),
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: subjectCorrects[subject],
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Doğru',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: subjectWrongs[subject],
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Yanlış',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),

            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _calculate,
              icon: const Icon(Icons.calculate_outlined),
              label: Text('$_selectedExam Tahmini Puan Hesapla'),
            ),

            if (_calculatedScore != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: scheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    Text(
                      '$_selectedExam Tahmini Puanınız',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: scheme.onSurfaceVariant,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$_calculatedScore',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            fontWeight: FontWeight.w900,
                            color: scheme.primary,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Chip(
                      label: Text(_badge),
                      backgroundColor: scheme.primary.withValues(alpha: 0.1),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Toplam Net: ${_totalNet.toStringAsFixed(2)}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
