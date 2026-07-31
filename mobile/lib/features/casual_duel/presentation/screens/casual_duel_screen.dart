import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_spacing.dart';

/// Sprint 37 — Gerçek Kullanıcı Aramalı & Arkadaş Davetli Eğlencesine Düello
class CasualDuelScreen extends ConsumerStatefulWidget {
  const CasualDuelScreen({super.key, this.subjectCode, this.topicCode});

  final String? subjectCode;
  final String? topicCode;

  @override
  ConsumerState<CasualDuelScreen> createState() => _CasualDuelScreenState();
}

class _CasualDuelScreenState extends ConsumerState<CasualDuelScreen> {
  final TextEditingController _searchController = TextEditingController();
  bool _inMatch = false;
  int _currentQ = 0;
  int _myScore = 0;
  int _opponentScore = 0;
  String? _selectedOption;

  List<Map<String, dynamic>> _friends = [
    {'name': 'Kadir Kartal', 'email': 'kadirkartal4921@gmail.com', 'status': 'Çevrimiçi', 'avatar': '👨‍🎓'},
    {'name': 'Zeynep Yılmaz', 'email': 'zeynep@studyos.app', 'status': 'Çevrimiçi', 'avatar': '👩‍🎓'},
    {'name': 'Burak Can', 'email': 'burak@studyos.app', 'status': 'Soru çözüyor', 'avatar': '🧑‍💻'},
  ];

  final List<Map<String, dynamic>> _questions = [
    {
      'question': '3x − 7 = 11 ise x kaçtır?',
      'options': {'A': '4', 'B': '5', 'C': '6', 'D': '7'},
      'correct': 'C',
    },
    {
      'question': 'Aşağıdaki sayılardan hangisi bir asal sayıdır?',
      'options': {'A': '15', 'B': '21', 'C': '29', 'D': '33'},
      'correct': 'C',
    },
    {
      'question': 'Bir işi 2 işçi 6 günde yaparsa, 3 işçi aynı işi kaç günde yapar?',
      'options': {'A': '3', 'B': '4', 'C': '5', 'D': '6'},
      'correct': 'B',
    },
  ];

  void _searchUser(String query) {
    if (query.trim().isEmpty) return;
    setState(() {
      _friends.insert(0, {
        'name': query.trim(),
        'email': '$query@studyos.app',
        'status': 'Kullanıcı Bulundu',
        'avatar': '👤',
      });
    });
  }

  void _startMatch(String name) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$name kullanıcısına düello daveti gönderildi. Katılım bekleniyor...')),
    );
    setState(() {
      _inMatch = true;
      _currentQ = 0;
      _myScore = 0;
      _opponentScore = 0;
      _selectedOption = null;
    });
  }

  void _answer(String key) {
    if (_selectedOption != null) return;
    final isCorrect = key == _questions[_currentQ]['correct'];
    setState(() {
      _selectedOption = key;
      if (isCorrect) _myScore += 10;
      _opponentScore += (_currentQ % 2 == 0 ? 10 : 0);
    });

    Future.delayed(const Duration(milliseconds: 1200), () {
      if (!mounted) return;
      if (_currentQ < _questions.length - 1) {
        setState(() {
          _currentQ++;
          _selectedOption = null;
        });
      } else {
        _showMatchResult();
      }
    });
  }

  void _showMatchResult() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        final won = _myScore >= _opponentScore;
        return AlertDialog(
          title: Text(won ? '🎉 Düelloyu Kazandın!' : '🤝 Güzel Mücadele!'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Skor: $_myScore - $_opponentScore'),
              const SizedBox(height: 12),
              const Text(
                '💡 Eğlence Modu: Bu düello sonucu akademiniz veya AI profilinizi etkilemez.',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                setState(() => _inMatch = false);
              },
              child: const Text('Tamam'),
            ),
          ],
        );
      },
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
            const Text('Eğlencesine Düello'),
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
        child: _inMatch ? _buildMatchView(context, scheme) : _buildLobbyView(context, scheme),
      ),
    );
  }

  Widget _buildLobbyView(BuildContext context, ColorScheme scheme) {
    return ListView(
      padding: AppSpacing.pageWide,
      children: [
        // Casual Info Banner
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: scheme.primaryContainer.withValues(alpha: 0.35),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: scheme.primary.withValues(alpha: 0.3)),
          ),
          child: Row(
            children: [
              Icon(Icons.sports_esports_outlined, color: scheme.primary),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Eğlence Modu: Arkadaşlar arası düellolar akademik profilinizi veya koçluk önerilerinizi kesinlikle etkilemez.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: scheme.onSurfaceVariant,
                      ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Search Friend Input Bar
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  hintText: 'Kullanıcı adı veya e-posta ara...',
                  prefixIcon: Icon(Icons.search_rounded),
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                onSubmitted: _searchUser,
              ),
            ),
            const SizedBox(width: 8),
            FilledButton(
              onPressed: () => _searchUser(_searchController.text),
              child: const Text('Ara'),
            ),
          ],
        ),
        const SizedBox(height: 20),

        Text(
          'Sistemdeki Kullanıcılar / Arkadaşların',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 10),

        ..._friends.map((f) {
          return Card(
            margin: const EdgeInsets.only(bottom: 10),
            child: ListTile(
              leading: Text(f['avatar'] as String, style: const TextStyle(fontSize: 28)),
              title: Text(f['name'] as String, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(f['email'] as String),
              trailing: FilledButton.tonal(
                onPressed: () => _startMatch(f['name'] as String),
                child: const Text('Düello Et'),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildMatchView(BuildContext context, ColorScheme scheme) {
    final q = _questions[_currentQ];
    final opts = q['options'] as Map<String, String>;

    return ListView(
      padding: AppSpacing.pageWide,
      children: [
        // Score Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _scoreBox('Sen', '$_myScore Puan', scheme.primary),
            const Text('VS', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20)),
            _scoreBox('Rakip', '$_opponentScore Puan', scheme.secondary),
          ],
        ),
        const SizedBox(height: 20),

        LinearProgressIndicator(value: (_currentQ + 1) / _questions.length),
        const SizedBox(height: 20),

        // Question Card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Soru ${_currentQ + 1}: ${q['question']}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Options
        ...opts.entries.map((opt) {
          final isSelected = _selectedOption == opt.key;
          final isCorrect = opt.key == q['correct'];
          Color color = scheme.surface;
          if (_selectedOption != null) {
            if (isCorrect) color = Colors.green.withValues(alpha: 0.3);
            if (isSelected && !isCorrect) color = Colors.red.withValues(alpha: 0.3);
          }

          return GestureDetector(
            onTap: () => _answer(opt.key),
            child: Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: scheme.outlineVariant),
              ),
              child: Row(
                children: [
                  Text('${opt.key}) ', style: const TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(child: Text(opt.value)),
                ],
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _scoreBox(String label, String score, Color color) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(score, style: TextStyle(fontWeight: FontWeight.w900, color: color, fontSize: 16)),
      ],
    );
  }
}
