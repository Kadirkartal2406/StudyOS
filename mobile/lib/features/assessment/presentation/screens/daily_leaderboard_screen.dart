import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/ds.dart';
import '../../data/assessment_remote_datasource.dart';

class DailyLeaderboardScreen extends ConsumerStatefulWidget {
  const DailyLeaderboardScreen({super.key, this.subjectCode});

  final String? subjectCode;

  @override
  ConsumerState<DailyLeaderboardScreen> createState() =>
      _DailyLeaderboardScreenState();
}

class _DailyLeaderboardScreenState
    extends ConsumerState<DailyLeaderboardScreen> {
  Map<String, dynamic>? _data;
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
      final data = await ref.read(assessmentDatasourceProvider).dailyLeaderboard(
            subjectCode: widget.subjectCode,
          );
      if (!mounted) return;
      setState(() {
        _data = data;
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
        _error = 'Sıralama yüklenemedi';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final scope = _data?['scope'] as String? ?? 'overall';
    final myRank = _data?['my_rank'];
    final myScore = _data?['my_score'];
    final entries = (_data?['entries'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: Text(scope == 'subject' ? 'Ders sıralaması' : 'Genel sıralama'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : ListView(
                  padding: AppSpacing.pageWide,
                  children: [
                    if (myRank != null)
                      StudyCard(
                        child: Text(
                          'Sıralaman: #$myRank'
                          '${myScore != null ? ' · ${ (myScore as num).toStringAsFixed(0)} puan' : ''}',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                      ),
                    const SizedBox(height: AppSpacing.md),
                    for (final e in entries)
                      ListTile(
                        leading: CircleAvatar(
                          child: Text('${e['rank']}'),
                        ),
                        title: Text(
                          e['nickname'] as String? ?? 'Öğrenci',
                          style: TextStyle(
                            fontWeight: (e['is_me'] as bool? ?? false)
                                ? FontWeight.w700
                                : FontWeight.w400,
                          ),
                        ),
                        trailing: Text(
                          (e['score'] as num?)?.toStringAsFixed(0) ?? '0',
                        ),
                      ),
                    if (entries.isEmpty)
                      const Padding(
                        padding: EdgeInsets.all(24),
                        child: Text('Henüz sıralama yok. İlk denemeyi sen çöz!'),
                      ),
                  ],
                ),
    );
  }
}
