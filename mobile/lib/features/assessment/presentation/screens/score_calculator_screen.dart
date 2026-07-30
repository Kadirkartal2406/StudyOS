import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_spacing.dart';

/// Sprint 33 — ÖSYM Tahmini Puan Hesaplama Ekranı (KPSS, TYT, AYT, LGS)
class ScoreCalculatorScreen extends ConsumerStatefulWidget {
  const ScoreCalculatorScreen({super.key});

  @override
  ConsumerState<ScoreCalculatorScreen> createState() => _ScoreCalculatorScreenState();
}

class _ScoreCalculatorScreenState extends ConsumerState<ScoreCalculatorScreen> {
  String _selectedExam = 'KPSS';
  
  final Map<String, TextEditingController> _correctControllers = {
    'Turkce': TextEditingController(text: '24'),
    'Matematik': TextEditingController(text: '20'),
    'Tarih': TextEditingController(text: '18'),
    'Cografya': TextEditingController(text: '12'),
  };

  final Map<String, TextEditingController> _wrongControllers = {
    'Turkce': TextEditingController(text: '4'),
    'Matematik': TextEditingController(text: '5'),
    'Tarih': TextEditingController(text: '3'),
    'Cografya': TextEditingController(text: '2'),
  };

  double? _calculatedScore;
  double _totalNet = 0.0;
  String _badge = '🥈 Altın Hedef';

  void _calculate() {
    double netSum = 0;
    int totalCorrect = 0;
    int totalWrong = 0;
    final penalty = _selectedExam == 'LGS' ? 3.0 : 4.0;

    _correctControllers.forEach((key, cController) {
      final wController = _wrongControllers[key];
      final correct = int.tryParse(cController.text) ?? 0;
      final wrong = int.tryParse(wController?.text ?? '0') ?? 0;
      totalCorrect += correct;
      totalWrong += wrong;
      final net = (correct - (wrong / penalty)).clamp(0.0, 100.0);
      netSum += net;
    });

    double score = 0;
    final maxScore = _selectedExam == 'KPSS' ? 100.0 : 500.0;

    if (_selectedExam == 'KPSS') {
      score = (40.0 + (netSum * 0.55)).clamp(0.0, 100.0);
    } else {
      score = (100.0 + (netSum * 3.3)).clamp(0.0, 500.0);
    }

    setState(() {
      _totalNet = netSum;
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

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tahmini Puan Hesaplama'),
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
                      'Hesaplanan değer ÖSYM katsayıları temel alınarak hesaplanmış Tahmini Puan\'dır. Kesin ÖSYM sınav sonucu değildir.',
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

            // Inputs Table
            ..._correctControllers.keys.map((subject) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Row(
                  children: [
                    Expanded(
                      flex: 3,
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
                        controller: _correctControllers[subject],
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Doğru',
                          dense: true,
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: _wrongControllers[subject],
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          labelText: 'Yanlış',
                          dense: true,
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
              label: const Text('Tahmini Puan Hesapla'),
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
                      'Tahmini Puanınız',
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
