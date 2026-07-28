import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../assessment/data/assessment_remote_datasource.dart';
import '../../../assessment/presentation/utils/level_test_count.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../providers/first_run_phase_provider.dart';
import '../providers/learning_profile_provider.dart';

/// RC3 D1 — yumuşak zorunlu seviye testi + geçici plan uyarısı.
class SetupCalibrationScreen extends ConsumerStatefulWidget {
  const SetupCalibrationScreen({super.key});

  @override
  ConsumerState<SetupCalibrationScreen> createState() =>
      _SetupCalibrationScreenState();
}

class _SetupCalibrationScreenState
    extends ConsumerState<SetupCalibrationScreen> {
  bool _loading = false;
  String? _error;

  String get _name {
    final auth = ref.read(authProvider);
    return switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => 'dostum',
    };
  }

  Future<void> _start() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final ds = ref.read(assessmentDatasourceProvider);
      final overview = await ds.overview();
      final next = overview.subjects
          .cast<AssessmentProgressItemEntity?>()
          .firstWhere(
            (s) => s != null && !s.completed,
            orElse: () =>
                overview.subjects.isEmpty ? null : overview.subjects.first,
          );
      if (!mounted) return;
      if (next == null || next.completed) {
        await ref.read(firstRunPhaseProvider.notifier).setPhase('preparing');
        if (!mounted) return;
        context.go('/setup/preparing');
        return;
      }
      final profile = ref.read(learningProfileProvider).valueOrNull;
      final exam =
          profile?.activeExamType ?? profile?.primaryExamType ?? 'kpss';
      final count = levelTestCountForExam(exam);
      await ref
          .read(firstRunPhaseProvider.notifier)
          .setPhase('calibration_active');
      if (!mounted) return;
      context.go(
        '/assessment/branch/start'
        '?subject_code=${Uri.encodeComponent(next.subjectCode)}'
        '&kind=calibration'
        '&setup=1'
        '&count=$count',
      );
    } on AppException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Seviye testi başlatılamadı');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _skipForNow() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Şimdilik geçici plan'),
        content: const Text(
          'Şu an yalnızca sohbette anlattığın bilgilerle geçici bir '
          'çalışma planı kuracağız.\n\n'
          'Seviye testini tamamladığında planın gerçek seviyene göre '
          'gelişecek.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Vazgeç'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Geçici planla devam'),
          ),
        ],
      ),
    );
    if (ok != true || !mounted) return;
    await ref.read(firstRunPhaseProvider.notifier).setPhase('preparing');
    if (!mounted) return;
    context.go('/setup/preparing');
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final exam =
        (profile?.activeExamType ?? profile?.primaryExamType ?? 'sınav')
            .toUpperCase();
    final count = levelTestCountForExam(
      profile?.activeExamType ?? profile?.primaryExamType,
    );

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              Icon(
                Icons.quiz_outlined,
                size: 56,
                color: scheme.primary,
              ),
              const SizedBox(height: 20),
              Text(
                'Seviye testi, $_name',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 12),
              Text(
                '$exam için ders ders seviye testi yapacağız. '
                'Her derste yaklaşık $count soru var — aynı sınava hazırlanan '
                'herkese aynı ölçüm seti gösterilir.\n\n'
                'Seviyen buradan başlar; deneme ve çalışma verilerinle zamanla güncellenir.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.4,
                    ),
              ),
              if (_error != null) ...[
                const SizedBox(height: 16),
                Text(_error!, style: TextStyle(color: scheme.error)),
              ],
              const Spacer(),
              FilledButton(
                onPressed: _loading ? null : _start,
                child: _loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Seviye testine başla'),
              ),
              const SizedBox(height: 8),
              Text(
                'Planın gerçek seviyene göre kurulur',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: _loading ? null : _skipForNow,
                child: const Text('Şimdilik geç'),
              ),
              Text(
                'Mevcut bilgilerinle geçici plan · seviye testiyle gelişir',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
