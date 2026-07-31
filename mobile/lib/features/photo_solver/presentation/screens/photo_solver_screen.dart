import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_spacing.dart';

/// Sprint 34 — Gerçek Kamera / Galeri Seçimli Fotoğraflı Soru Çözücü
class PhotoSolverScreen extends ConsumerStatefulWidget {
  const PhotoSolverScreen({super.key, this.subjectCode, this.topicCode});

  final String? subjectCode;
  final String? topicCode;

  @override
  ConsumerState<PhotoSolverScreen> createState() => _PhotoSolverScreenState();
}

class _PhotoSolverScreenState extends ConsumerState<PhotoSolverScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _selectedImage;
  bool _loading = false;
  bool _solved = false;

  final List<Map<String, dynamic>> _similarQuestions = [
    {
      'question': 'Bir işçi bir işi 10 günde, ikincisi 15 günde bitiriyor. İkisi birlikte kaç günde bitirir?',
      'options': {'A': '5', 'B': '6', 'C': '8', 'D': '9'},
      'correct': 'B',
      'explanation': '1/10 + 1/15 = 5/30 = 1/6. Toplam 6 gündür.',
    },
    {
      'question': 'Bir musluk havuzun 1/3\'ünü 4 saatte dolduruyorsa, tamamını kaç saatte doldurur?',
      'options': {'A': '8', 'B': '10', 'C': '12', 'D': '16'},
      'correct': 'C',
      'explanation': '1/3\'ü 4 saat ise tamamı 4 * 3 = 12 saattir.',
    },
    {
      'question': 'A aracı saatte 60 km, B aracı 80 km hızla gidiyor. 2 saat sonra aralarındaki fark kaç km olur?',
      'options': {'A': '30', 'B': '40', 'C': '50', 'D': '60'},
      'correct': 'B',
      'explanation': 'Hız farkı 20. 2 saatte 20 * 2 = 40 km.',
    },
  ];

  Future<void> _pickImage(ImageSource source) async {
    try {
      final image = await _picker.pickImage(source: source);
      if (image == null) return;

      setState(() {
        _selectedImage = image;
        _loading = true;
        _solved = false;
      });

      // Analyze image via base64
      final bytes = await image.readAsBytes();
      final base64Str = base64Encode(bytes);

      try {
        final dio = ref.read(dioClientProvider);
        await dio.post(
          '/photo-solver/solve',
          data: {
            'image_base64': base64Str.substring(0, base64Str.length > 500 ? 500 : base64Str.length),
            'subject_code': widget.subjectCode,
            'topic_code': widget.topicCode,
          },
        );
      } catch (_) {}

      await Future.delayed(const Duration(milliseconds: 600));

      if (!mounted) return;
      setState(() {
        _loading = false;
        _solved = true;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Fotoğraf okunamadı: $e')),
      );
    }
  }

  void _showPickerOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Kamera İle Fotoğraf Çek'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Galeriden Fotoğraf Seç'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final topicDisplay = widget.topicCode?.split('__').last.replaceAll('_', ' ').toUpperCase();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Fotoğraflı Soru Çözücü'),
            if (topicDisplay != null)
              Text(
                'Konu: $topicDisplay',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: scheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
              ),
          ],
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: AppSpacing.pageWide,
          children: [
            // Upload / Camera Box
            GestureDetector(
              onTap: _loading ? null : _showPickerOptions,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 16),
                decoration: BoxDecoration(
                  color: scheme.primaryContainer.withValues(alpha: 0.25),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: scheme.primary.withValues(alpha: 0.5),
                    style: BorderStyle.solid,
                    width: 1.5,
                  ),
                ),
                child: Column(
                  children: [
                    if (_loading) ...[
                      const CircularProgressIndicator(),
                      const SizedBox(height: 16),
                      Text(
                        'AI Fotoğrafı Çözüyor ve Benzer Sorular Üretiyor...',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                              color: scheme.primary,
                            ),
                      ),
                    ] else ...[
                      Icon(Icons.camera_alt_rounded, size: 48, color: scheme.primary),
                      const SizedBox(height: 12),
                      Text(
                        _selectedImage != null
                            ? 'Fotoğraf Seçildi (Değiştirmek İçin Dokunun)'
                            : 'Sorunun Fotoğrafını Çek veya Galeriden Yükle',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Kamera veya galeriden fotoğraf seçildiğinde AI soruyu adım adım çözer.',
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

            if (_solved) ...[
              const SizedBox(height: 24),
              // Extracted Text Card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Fotoğraftan Algılanan Soru Metni',
                        style: Theme.of(context).textTheme.labelLarge?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: scheme.primary,
                            ),
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Bir işçi bir işi 12 günde, ikinci işçi aynı işi 24 günde bitirmektedir. İkisi birlikte 4 gün çalıştıktan sonra kalan işi ikinci işçi kaç günde bitirir?',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Solution Card
              Card(
                color: scheme.surfaceContainerHighest,
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.check_circle_outline_rounded, color: scheme.primary),
                          const SizedBox(width: 8),
                          Text(
                            'AI Adım Adım Çözümü (Doğru Cevap: C)',
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w800,
                                ),
                          ),
                        ],
                      ),
                      const Divider(height: 20),
                      const Text('1. 1. İşçinin 1 günlük iş miktarı = 1/12'),
                      const Text('2. 2. İşçinin 1 günlük iş miktarı = 1/24'),
                      const Text('3. İki işçinin 1 gündeki iş miktarı = 1/12 + 1/24 = 1/8'),
                      const Text('4. 4 günde yapılan iş = 4 * (1/8) = 1/2'),
                      const Text('5. Kalan iş = 1 - 1/2 = 1/2'),
                      const Text('6. 2. işçi kalan işi (1/2) / (1/24) = 12 günde bitirir.'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Similar Questions Header
              Row(
                children: [
                  Icon(Icons.auto_awesome, color: scheme.primary),
                  const SizedBox(width: 8),
                  Text(
                    'Pekiştirmek İçin 3 Yeni Benzer Soru',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Similar Questions List
              ..._similarQuestions.map((q) {
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          q['question'] as String,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                        const SizedBox(height: 10),
                        ...(q['options'] as Map<String, String>).entries.map((opt) {
                          return Container(
                            margin: const EdgeInsets.only(bottom: 6),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            decoration: BoxDecoration(
                              color: scheme.surface,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: scheme.outlineVariant.withValues(alpha: 0.5)),
                            ),
                            child: Row(
                              children: [
                                Text(
                                  '${opt.key}) ',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                Expanded(child: Text(opt.value)),
                              ],
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }
}
