import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../features/auth/presentation/providers/auth_state.dart';

/// RC3 — Açılış WOW (3–4 sn), sonra sohbet.
class SetupWowScreen extends ConsumerStatefulWidget {
  const SetupWowScreen({super.key});

  @override
  ConsumerState<SetupWowScreen> createState() => _SetupWowScreenState();
}

class _SetupWowScreenState extends ConsumerState<SetupWowScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _c;
  late final Animation<double> _fade;
  late final Animation<Offset> _slide;
  int _beat = 0;

  @override
  void initState() {
    super.initState();
    _c = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _fade = CurvedAnimation(parent: _c, curve: Curves.easeOut);
    _slide = Tween<Offset>(
      begin: const Offset(0, 0.08),
      end: Offset.zero,
    ).animate(_fade);
    _runBeats();
  }

  Future<void> _runBeats() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    if (!mounted) return;
    setState(() => _beat = 1);
    _c.forward(from: 0);
    await Future<void>.delayed(const Duration(milliseconds: 1400));
    if (!mounted) return;
    setState(() => _beat = 2);
    _c.forward(from: 0);
    await Future<void>.delayed(const Duration(milliseconds: 1600));
    if (!mounted) return;
    setState(() => _beat = 3);
    _c.forward(from: 0);
    await Future<void>.delayed(const Duration(milliseconds: 1200));
    if (!mounted) return;
    context.go('/onboarding');
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => '',
    };
    final scheme = Theme.of(context).colorScheme;

    String line = 'StudyOS';
    if (_beat == 2 && name.isNotEmpty) line = 'Merhaba $name';
    if (_beat == 2 && name.isEmpty) line = 'Merhaba';
    if (_beat >= 3) {
      line = 'Sana özel bir çalışma sistemi kuracağız.';
    }

    return Scaffold(
      backgroundColor: scheme.surface,
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: FadeTransition(
              opacity: _fade,
              child: SlideTransition(
                position: _slide,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (_beat <= 1)
                      Icon(
                        Icons.auto_awesome,
                        size: 48,
                        color: scheme.primary,
                      ),
                    if (_beat <= 1) const SizedBox(height: 20),
                    Text(
                      line,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                            height: 1.25,
                          ),
                    ),
                    if (_beat >= 3) ...[
                      const SizedBox(height: 28),
                      FilledButton(
                        onPressed: () => context.go('/onboarding'),
                        child: const Text('Başla'),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
