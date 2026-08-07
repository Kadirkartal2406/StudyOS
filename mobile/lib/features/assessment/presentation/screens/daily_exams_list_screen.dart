import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../data/assessment_remote_datasource.dart';

class DailyExamsListScreen extends ConsumerStatefulWidget {
  const DailyExamsListScreen({super.key});

  @override
  ConsumerState<DailyExamsListScreen> createState() => _DailyExamsListScreenState();
}

class _DailyExamsListScreenState extends ConsumerState<DailyExamsListScreen> {
  List<Map<String, dynamic>>? _history;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await ref.read(assessmentDatasourceProvider).dailyHistory();
      if (!mounted) return;
      setState(() {
        _history = data;
        _loading = false;
      });
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.message;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Geçmiş denemeler yüklenemedi';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Günün Denemesi Geçmişi'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _history == null || _history!.isEmpty
                  ? const Center(child: Text('Henüz geçmiş denemeniz bulunmuyor.'))
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.builder(
                        padding: AppSpacing.pageWide,
                        itemCount: _history!.length,
                        itemBuilder: (context, index) {
                          final item = _history![index];
                          final dateStr = item['challenge_date'] as String? ?? '';
                          final score = item['score'] as num?;
                          final studyosScore = item['studyos_score'] as num?;
                          final studyosRank = item['studyos_rank'] as int?;
                          final isOfficial = item['is_official'] as bool? ?? false;
                          final osymEstimations = item['osym_estimations'] as Map<String, dynamic>?;
                          final status = item['status'] as String?;
                          final isToday = index == 0; // Assuming it's ordered by date descending
                          
                          DateTime? dateObj;
                          try {
                            if (dateStr.isNotEmpty) {
                              dateObj = DateTime.parse(dateStr);
                            }
                          } catch (_) {}
                          
                          final displayDate = dateObj != null 
                              ? DateFormat('d MMMM yyyy', 'tr').format(dateObj) 
                              : dateStr;

                          String scoreText = '-- Puan';
                          if (studyosScore != null) {
                            scoreText = '${studyosScore.toStringAsFixed(1)} StudyOS Puanı';
                            if (!isOfficial) scoreText += ' (Tahmini)';
                          } else if (score != null) {
                            scoreText = '${(score * 100).toStringAsFixed(1)}% Başarı';
                          } else if (status == 'pending') {
                            scoreText = 'Çözülmedi';
                          } else if (status == 'active') {
                            scoreText = 'Devam Ediyor';
                          }

                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                              side: isToday 
                                  ? BorderSide(color: theme.colorScheme.primary, width: 2)
                                  : BorderSide.none,
                            ),
                            child: ListTile(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                              leading: Icon(
                                isToday ? Icons.star : Icons.history,
                                color: isToday ? theme.colorScheme.primary : Colors.grey,
                                size: 28,
                              ),
                              title: Text(
                                isToday ? 'Bugünün Denemesi' : displayDate,
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              subtitle: Text(
                                'Durum: $scoreText',
                                style: TextStyle(
                                  color: status == 'submitted' || score != null 
                                      ? Colors.green 
                                      : (status == 'active' ? Colors.orange : Colors.grey),
                                ),
                              ),
                              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                              onTap: () {
                                if (status == 'submitted' && studyosScore != null) {
                                  _showResultBottomSheet(
                                    context, 
                                    displayDate, 
                                    studyosScore, 
                                    studyosRank, 
                                    isOfficial, 
                                    osymEstimations
                                  );
                                  return;
                                }
                                if (isToday) {
                                  // For today's challenge, route to the hub
                                  context.push('/assessment/daily');
                                } else {
                                  final sessionId = item['session_id'];
                                  if (sessionId != null) {
                                    context.push('/assessment/session/$sessionId');
                                  } else {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(content: Text('Bu deneme başlatılmamış')),
                                    );
                                  }
                                }
                              },
                            ),
                          );
                        },
                      ),
                    ),
    );
  }

  void _showResultBottomSheet(
    BuildContext context, 
    String date, 
    num score, 
    int? rank, 
    bool isOfficial, 
    Map<String, dynamic>? osym
  ) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      isScrollControlled: true,
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(24.0).copyWith(bottom: MediaQuery.of(ctx).padding.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                '$date Sonuçları',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              if (!isOfficial)
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'Bu sonuç tahminidir. Denemeyi saat 21:59\'dan sonra çözdüğünüz için resmi sıralamaya dahil edilmediniz.',
                    style: TextStyle(color: Colors.orange, fontSize: 12),
                    textAlign: TextAlign.center,
                  ),
                ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      'StudyOS Puanı', 
                      score.toStringAsFixed(1), 
                      Icons.score, 
                      Colors.blue
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildStatCard(
                      'Sıralama', 
                      rank != null ? '#$rank' : '--', 
                      Icons.leaderboard, 
                      Colors.purple
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              const Text('ÖSYM Tahmini Puanları', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 12),
              if (osym == null || osym.isEmpty)
                const Text('ÖSYM tahmini bulunamadı', style: TextStyle(color: Colors.grey)),
              if (osym != null && osym.isNotEmpty)
                ...osym.entries.map((e) {
                  final data = e.value as Map<String, dynamic>? ?? {};
                  final s = data['score'] as num?;
                  final r = data['rank'] as int?;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('YKS ${e.key}', style: const TextStyle(fontWeight: FontWeight.w500)),
                        Text('${s?.toStringAsFixed(2) ?? "--"} Puan ${r != null ? "(#$r)" : ""}'),
                      ],
                    ),
                  );
                }),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Kapat'),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }
}
