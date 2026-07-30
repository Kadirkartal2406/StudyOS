import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_spacing.dart';

/// Sprint 35 — Kamera İle Optik Form Okuyucu & Otomatik Sonuç Ekranı
class CameraOpticalScannerScreen extends ConsumerStatefulWidget {
  const CameraOpticalScannerScreen({super.key});

  @override
  ConsumerState<CameraOpticalScannerScreen> createState() => _CameraOpticalScannerScreenState();
}

class _CameraOpticalScannerScreenState extends ConsumerState<CameraOpticalScannerScreen> {
  bool _scanning = false;
  bool _scanned = false;
  String _selectedExam = 'KPSS';

  // Result metrics
  int _correct = 16;
  int _wrong = 4;
  int _blank = 0;
  double _net = 15.0;
  double _estimatedScore = 78.5;
  String _badge = '🥈 Altın Hedef';

  void _simulateCameraScan() async {
    setState(() => _scanning = true);
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;
    setState(() {
      _scanning = false;
      _scanned = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Optik Form Okuyucu'),
      ),
      body: SafeArea(
        child: ListView(
          padding: AppSpacing.pageWide,
          children: [
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
                setState(() => _selectedExam = val.first);
              },
            ),
            const SizedBox(height: 16),

            // Camera Scanner Box Guide
            GestureDetector(
              onTap: _scanning ? null : _simulateCameraScan,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: scheme.surfaceContainerHighest.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: scheme.primary.withValues(alpha: 0.6),
                    width: 2.0,
                  ),
                ),
                child: Column(
                  children: [
                    if (_scanning) ...[
                      const CircularProgressIndicator(),
                      const SizedBox(height: 16),
                      Text(
                        'Kamera Hizalanıyor: Kutucuklar Okunuyor...',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: scheme.primary,
                            ),
                      ),
                    ] else ...[
                      Icon(Icons.crop_free_rounded, size: 64, color: scheme.primary),
                      const SizedBox(height: 12),
                      Text(
                        'Optik Formu Çerçeveye Hizala ve Tara',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Kamera işaretlenmiş A-B-C-D-E kutucuklarını otomatik okur ve ÖSYM puanını hesaplar.',
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: scheme.onSurfaceVariant,
                            ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            if (_scanned) ...[
              const SizedBox(height: 24),
              // Results Header Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: scheme.primaryContainer.withValues(alpha: 0.45),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: scheme.primary.withValues(alpha: 0.4)),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Optik Tarama Sonucu',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w800,
                              ),
                        ),
                        Chip(
                          label: Text(_badge),
                          backgroundColor: scheme.surface,
                        ),
                      ],
                    ),
                    const Divider(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _metricChip(context, 'Doğru', '$_correct', Colors.green),
                        _metricChip(context, 'Yanlış', '$_wrong', Colors.red),
                        _metricChip(context, 'Net', '${_net.toStringAsFixed(2)}', scheme.primary),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Tahmini Puan: $_estimatedScore',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.w900,
                            color: scheme.primary,
                          ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Detected Choice Sheet Grid
              Text(
                'Algılanan Cevap Anahtarı Grid\'i',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: List.generate(20, (index) {
                  final qNum = index + 1;
                  final choices = ['A', 'B', 'C', 'D', 'E'];
                  final ans = choices[index % 5];
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: scheme.surface,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: scheme.outlineVariant),
                    ),
                    child: Text(
                      'S$qNum: $ans',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  );
                }),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _metricChip(BuildContext context, String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w900,
                color: color,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
      ],
    );
  }
}
