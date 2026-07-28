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
  const DailyChallengeSubjectsScreen({super.key});

  @override
  ConsumerState<DailyChallengeSubjectsScreen> createState() =>
      _DailyChallengeSubjectsScreenState();
}

class _DailyChallengeSubjectsScreenState
    extends ConsumerState<DailyChallengeSubjectsScreen> {
  Map<String, dynamic>? _daily;
  String? _examType;
  String? _error;
  bool _loading = true;
  bool _busy = false;

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
      final data = await ref.read(assessmentDatasourceProvider).dailyBundle();
      if (!mounted) return;
      final dailyRaw = data['daily'];
      Map<String, dynamic>? daily;
      if (dailyRaw is Map<String, dynamic>) {
        daily = dailyRaw;
      } else if (dailyRaw is Map) {
        daily = dailyRaw.map((k, v) => MapEntry(k.toString(), v));
      }
      setState(() {
        _daily = daily;
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

  Future<AssessmentSessionEntity?> _ensureSession({bool waitUntilReady = false}) async {
    final ds = ref.read(assessmentDatasourceProvider);
    final session = await ds.startDaily();
    if (!waitUntilReady) return session;
    if (session.status == 'ready' && session.questions.isNotEmpty) {
      return session;
    }
    if (session.status == 'submitted') return session;
    // Pack yoksa uzun poll yapma — kullanıcıya net mesaj
    throw const UnknownException(
      message:
          'Günün denemesi henüz hazır değil. '
          'Sorular her gece 00:00’da Gemini ile üretilir.',
    );
  }

  Future<void> _solveInApp() async {
    setState(() => _busy = true);
    try {
      final session = await _ensureSession(waitUntilReady: true);
      if (!mounted || session == null) return;
      context.push('/assessment/session/${session.id}');
    } on AppException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _downloadPdf() async {
    setState(() => _busy = true);
    try {
      final session = await _ensureSession(waitUntilReady: true);
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
      final path = await savePdfBytes(bytes, 'gunun-denemesi.pdf');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('PDF indirildi: $path')),
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

  Future<void> _openOptical() async {
    setState(() => _busy = true);
    try {
      final session = await _ensureSession();
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
    final title = _daily?['title'] as String? ?? 'Günün Denemesi';
    final status = _daily?['status'] as String? ?? 'available';
    final count = _daily?['requested_count'] as int?;
    final exam = (_examType ?? '').toUpperCase();
    final completed = status == 'completed';

    return ListView(
      padding: AppSpacing.pageWide,
      children: [
        StudyCard(
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
                    ? 'Aktif sınavındaki tüm dersler, resmi soru sayılarıyla.'
                    : '$exam — tüm dersler, resmi soru sayılarıyla'
                        '${count != null ? ' ($count soru)' : ''}.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                _statusLabel(status),
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        FilledButton.icon(
          onPressed: _busy || completed ? null : _solveInApp,
          icon: const Icon(Icons.play_arrow_rounded),
          label: Text(completed ? 'Tamamlandı' : 'Uygulamada çöz'),
        ),
        const SizedBox(height: AppSpacing.sm),
        FilledButton.tonalIcon(
          onPressed: _busy ? null : _downloadPdf,
          icon: const Icon(Icons.picture_as_pdf_outlined),
          label: const Text('PDF indir'),
        ),
        const SizedBox(height: AppSpacing.sm),
        OutlinedButton.icon(
          onPressed: _busy || completed ? null : _openOptical,
          icon: const Icon(Icons.grid_on_outlined),
          label: const Text('Optik ile gir'),
        ),
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
