import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/ds.dart';
import '../../data/assessment_remote_datasource.dart';
import '../utils/pdf_download.dart';

/// Sprint 23 — Günün Denemesi kitapçık hub (çöz / PDF / optik).
class DailyChallengeSubjectsScreen extends ConsumerStatefulWidget {
  final String? sessionId;
  const DailyChallengeSubjectsScreen({super.key, this.sessionId});

  @override
  ConsumerState<DailyChallengeSubjectsScreen> createState() =>
      _DailyChallengeSubjectsScreenState();
}

class _DailyChallengeSubjectsScreenState
    extends ConsumerState<DailyChallengeSubjectsScreen> {
  List<Map<String, dynamic>> _dailies = [];
  String? _examType;
  String? _error;
  bool _loading = true;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Map<String, dynamic> _asStringMap(dynamic raw) {
    if (raw is Map<String, dynamic>) return raw;
    if (raw is Map) {
      return raw.map((k, v) => MapEntry(k.toString(), v));
    }
    return {};
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await ref.read(assessmentDatasourceProvider).dailyBundle();
      if (!mounted) return;
      final rawList = data['dailies'];
      final items = <Map<String, dynamic>>[];
      if (rawList is List) {
        for (final row in rawList) {
          final m = _asStringMap(row);
          if (m.isNotEmpty) items.add(m);
        }
      }
      if (items.isEmpty) {
        final daily = _asStringMap(data['daily']);
        if (daily.isNotEmpty) items.add(daily);
      }
      if (widget.sessionId != null && items.isNotEmpty) {
        items.first['session_id'] = widget.sessionId;
      }
      setState(() {
        _dailies = items;
        _examType = data['exam_type'] as String?;
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
        _error = 'Günün denemesi yüklenemedi';
        _loading = false;
      });
    }
  }

  Future<AssessmentSessionEntity?> _ensureSession(
    Map<String, dynamic> daily, {
    bool waitUntilReady = false,
  }) async {
    final ds = ref.read(assessmentDatasourceProvider);
    if (widget.sessionId != null) {
      return ds.getSession(widget.sessionId!);
    }
    final bookletExam = (daily['exam_type'] as String?)?.trim();
    final session = await ds.startDaily(bookletExam: bookletExam);
    if (!waitUntilReady) return session;
    if (session.status == 'ready' && session.questions.isNotEmpty) {
      return session;
    }
    if (session.status == 'submitted') return session;
    throw const UnknownException(
      message:
          'Günün denemesi henüz hazır değil. '
          'Sorular gece üretilir; hazır olunca tekrar dene.',
    );
  }

  Future<void> _solveInApp(Map<String, dynamic> daily) async {
    setState(() => _busy = true);
    try {
      final session = await _ensureSession(daily, waitUntilReady: true);
      if (!mounted || session == null) return;
      context.push('/assessment/session/${session.id}');
    } on AppException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _downloadPdf(Map<String, dynamic> daily) async {
    setState(() => _busy = true);
    try {
      final session = await _ensureSession(daily, waitUntilReady: true);
      if (!mounted || session == null) return;
      if (session.questions.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('PDF için sorular henüz hazır değil')),
        );
        return;
      }
      final bytes = await ref
          .read(assessmentDatasourceProvider)
          .downloadSessionPdf(session.id);
      final exam = (daily['exam_type'] as String? ?? _examType ?? '').trim();
      final challengeDate = parseChallengeDate(daily['challenge_date']);
      final saved = await saveDailyBookletPdf(
        bytes: bytes,
        examType: exam.isEmpty ? 'Deneme' : exam,
        challengeDate: challengeDate,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            saved.sharedViaSheet
                ? '✓ Deneme indirildi — paylaşım menüsünden Dosyalar’a kaydedebilirsin'
                : '✓ Deneme indirildi',
          ),
          action: saved.canOpen && !saved.sharedViaSheet
              ? SnackBarAction(
                  label: 'PDF\'yi Aç',
                  onPressed: () async {
                    try {
                      await openSavedPdf(saved);
                    } catch (e) {
                      if (!mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('PDF açılamadı: $e')),
                      );
                    }
                  },
                )
              : null,
          duration: const Duration(seconds: 5),
        ),
      );
      await _load();
    } on AppException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('PDF indirilemedi: $e')),
      );
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _openOptical(Map<String, dynamic> daily) async {
    setState(() => _busy = true);
    try {
      final session = await _ensureSession(daily, waitUntilReady: true);
      if (!mounted || session == null) return;
      if (session.status == 'submitted') {
        context.push('/assessment/session/${session.id}');
        return;
      }
      context.push('/assessment/daily/optical?session_id=${session.id}');
    } on AppException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Günün Denemesi')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(_error!, textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: _load,
                          child: const Text('Tekrar dene'),
                        ),
                      ],
                    ),
                  ),
                )
              : _buildBody(context),
    );
  }

  Widget _buildBody(BuildContext context) {
    final profileExam = (_examType ?? '').toUpperCase();
    if (_dailies.isEmpty) {
      return const Center(child: Text('Bugün yayınlanacak deneme yok.'));
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: AppSpacing.pageWide,
      children: [
        if (profileExam.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.md),
            child: Text(
              profileExam == 'YKS'
                  ? 'YKS — bugün TYT ve AYT denemeleri ayrı yayınlanır.'
                  : '$profileExam — resmi soru sayılarıyla günlük deneme.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        for (var i = 0; i < _dailies.length; i++) ...[
          if (i > 0) const SizedBox(height: AppSpacing.md),
          _buildDailyCard(context, _dailies[i]),
        ],
        const SizedBox(height: AppSpacing.md),
        Text(
          'PDF’yi indirip kâğıtta çözebilir, sonra optik formla '
          'cevaplarını sisteme girebilirsin. İstersen uygulamada da çözebilirsin.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: AppSpacing.lg),
        OutlinedButton.icon(
          onPressed: () => context.push('/assessment/daily/leaderboard'),
          icon: const Icon(Icons.leaderboard_outlined),
          label: const Text('Sıralamayı gör'),
        ),
      ],
      ),
    );
  }

  Widget _buildDailyCard(BuildContext context, Map<String, dynamic> daily) {
    final title = daily['title'] as String? ?? 'Günün Denemesi';
    final status = daily['status'] as String? ?? 'available';
    final count = daily['requested_count'] as int?;
    final exam = (daily['exam_type'] as String? ?? '').toUpperCase();
    final completed = status == 'completed';
    final generating = status == 'generating';

    return StudyCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            exam.isEmpty
                ? 'Resmi soru sayılarıyla tam deneme'
                : '$exam — resmi soru sayılarıyla'
                    '${count != null ? ' ($count soru)' : ''}.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            _statusLabel(status),
            style: Theme.of(context).textTheme.labelLarge,
          ),
          const SizedBox(height: AppSpacing.md),
          FilledButton.icon(
            onPressed: _busy || completed || generating ? null : () => _solveInApp(daily),
            icon: const Icon(Icons.play_arrow_rounded),
            label: Text(
              completed
                  ? 'Tamamlandı'
                  : generating
                      ? 'Hazırlanıyor'
                      : 'Uygulamada çöz',
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          FilledButton.tonalIcon(
            onPressed: _busy || generating ? null : () => _downloadPdf(daily),
            icon: const Icon(Icons.picture_as_pdf_outlined),
            label: const Text('PDF indir'),
          ),
          const SizedBox(height: AppSpacing.sm),
          OutlinedButton.icon(
            onPressed: _busy || completed || generating
                ? null
                : () => _openOptical(daily),
            icon: const Icon(Icons.grid_on_outlined),
            label: const Text('Optik ile gir'),
          ),
        ],
      ),
    );
  }

  String _statusLabel(String? status) {
    return switch (status) {
      'completed' => 'Durum: Tamamlandı',
      'generating' => 'Durum: Hazırlanıyor…',
      'available' => 'Durum: Hazır',
      _ => 'Durum: Bekleniyor',
    };
  }
}
