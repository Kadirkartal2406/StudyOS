import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../adaptive_planner/presentation/providers/planner_provider.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../providers/first_run_phase_provider.dart';
import '../providers/learning_profile_provider.dart';

/// RC3 — animasyonlu “sistem hazırlanıyor”.
class SetupPreparingScreen extends ConsumerStatefulWidget {
  const SetupPreparingScreen({super.key});

  @override
  ConsumerState<SetupPreparingScreen> createState() =>
      _SetupPreparingScreenState();
}

class _SetupPreparingScreenState extends ConsumerState<SetupPreparingScreen>
    with SingleTickerProviderStateMixin {
  static const _steps = [
    'Hedefin ve süren analiz ediliyor',
    'Derslerin haritası çıkarılıyor',
    'Seviye testi / sohbet verisi işleniyor',
    'Günlük plan yazılıyor',
    'Tekrar ritmi ayarlanıyor',
    'AI seni tanıyor',
  ];

  int _done = 0;
  bool _failed = false;
  late final AnimationController _pulse;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
    WidgetsBinding.instance.addPostFrameCallback((_) => _run());
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  Future<void> _run() async {
    try {
      for (var i = 0; i < _steps.length; i++) {
        await Future<void>.delayed(const Duration(milliseconds: 950));
        if (!mounted) return;
        setState(() => _done = i + 1);

        if (i == 3) {
          try {
            final profile = ref.read(learningProfileProvider).valueOrNull;
            final exam = profile?.activeExamType ??
                profile?.primaryExamType ??
                'kpss';
            final net = profile?.examTargets.isNotEmpty == true
                ? (profile!.examTargets.first.targetNet ?? 90.0)
                : 90.0;
            final days = profile?.availableDays.isNotEmpty == true
                ? profile!.availableDays
                : <int>[0, 1, 2, 3, 4];
            final hours = profile?.availableHours ?? 2.5;
            await ref.read(plannerProvider.notifier).generate(
                  targetExam: exam,
                  targetNet: net,
                  availableDays: days,
                  availableHours: hours,
                );
          } catch (_) {}
        }
      }
      await ref
          .read(firstRunPhaseProvider.notifier)
          .setPhase('system_summary');
      if (!mounted) return;
      context.go('/setup/system-summary');
    } catch (_) {
      if (!mounted) return;
      setState(() => _failed = true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final progress = _done / _steps.length;
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              Text(
                name.isEmpty
                    ? 'Sana özel çalışma sistemi hazırlanıyor'
                    : '$name, sana özel çalışma sistemi hazırlanıyor',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 24),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: progress.clamp(0.05, 1.0),
                  minHeight: 8,
                ),
              ),
              const SizedBox(height: 28),
              for (var i = 0; i < _steps.length; i++)
                Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: Row(
                    children: [
                      if (i < _done)
                        Icon(Icons.check_circle, color: scheme.primary, size: 22)
                      else if (i == _done)
                        FadeTransition(
                          opacity: _pulse,
                          child: Icon(
                            Icons.radio_button_checked,
                            color: scheme.primary,
                            size: 22,
                          ),
                        )
                      else
                        Icon(
                          Icons.radio_button_unchecked,
                          color: scheme.outline,
                          size: 22,
                        ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _steps[i],
                          style: TextStyle(
                            fontWeight: i <= _done
                                ? FontWeight.w600
                                : FontWeight.w400,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              if (_failed) ...[
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () {
                    setState(() {
                      _failed = false;
                      _done = 0;
                    });
                    _run();
                  },
                  child: const Text('Tekrar dene'),
                ),
              ],
              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }
}
