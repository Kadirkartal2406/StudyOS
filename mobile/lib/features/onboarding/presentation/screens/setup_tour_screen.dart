import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../adaptive_planner/presentation/providers/planner_provider.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../dashboard/presentation/providers/dashboard_provider.dart';
import '../../../dashboard/presentation/providers/dashboard_state.dart';
import '../providers/first_run_phase_provider.dart';
import '../providers/learning_profile_provider.dart';
import '../welcome/exam_calendar.dart';

/// RC3.5 — Kişiselleştirilmiş tam ekran ürün tanıtımı (tooltip değil).
class SetupTourScreen extends ConsumerStatefulWidget {
  const SetupTourScreen({super.key});

  @override
  ConsumerState<SetupTourScreen> createState() => _SetupTourScreenState();
}

class _SetupTourScreenState extends ConsumerState<SetupTourScreen>
    with SingleTickerProviderStateMixin {
  int _page = 0;
  late final AnimationController _enter;

  @override
  void initState() {
    super.initState();
    _enter = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 420),
    )..forward();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(dashboardProvider.notifier).retry();
    });
  }

  @override
  void dispose() {
    _enter.dispose();
    super.dispose();
  }

  String get _name {
    final auth = ref.read(authProvider);
    return switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => 'dostum',
    };
  }

  Future<void> _finish() async {
    await ref.read(firstRunPhaseProvider.notifier).setPhase('done');
    if (!mounted) return;
    context.go('/dashboard');
  }

  void _next(int total) {
    if (_page >= total - 1) {
      _finish();
      return;
    }
    setState(() {
      _page++;
      _enter
        ..reset()
        ..forward();
    });
  }

  void _back() {
    if (_page == 0) return;
    setState(() {
      _page--;
      _enter
        ..reset()
        ..forward();
    });
  }

  List<_TourCard> _buildCards({
    required String examLabel,
    required String? branch,
    required int? daysLeft,
    required int? dailyMinutes,
    required String? weakHint,
    required String? nextTask,
    required List<String> todayBlocks,
  }) {
    final goalLine = [
      examLabel,
      if (branch != null && branch.isNotEmpty) branch,
    ].join(' ');
    final daysLine = daysLeft != null && daysLeft > 0
        ? '$daysLeft gün kaldı'
        : 'tarihini seninle takip edeceğiz';
    final hoursLine = dailyMinutes == null
        ? 'günlük ritmine'
        : 'günlük ~${(dailyMinutes / 60).toStringAsFixed(dailyMinutes % 60 == 0 ? 0 : 1)} saatine';
    final weakLine = (weakHint != null && weakHint.isNotEmpty)
        ? weakHint
        : 'gelişime açık derslerin';
    final taskLine =
        (nextTask != null && nextTask.isNotEmpty) ? nextTask : 'ilk görevin';

    return [
      _TourCard(
        kind: _TourKind.welcome,
        title: 'Her şey hazır.',
        body:
            'Artık seni tanıyorum, $_name.\n\n'
            'Hedefin:\n$goalLine\n\n'
            'Sınava\n$daysLine.\n\n'
            'Buna göre sana özel çalışma sistemi hazırladım.',
        cta: 'Nasıl çalışacağını göster',
      ),
      _TourCard(
        kind: _TourKind.todaySpotlight,
        title: 'Bugün',
        spotlightLabel: 'Sıradaki İş',
        spotlightValue: taskLine,
        body:
            'Burası her gün ilk açacağın ekran.\n\n'
            'Her sabah sana sadece o gün yapman gereken işleri göstereceğiz.\n\n'
            'Ne çalışacağını düşünmene gerek kalmayacak.\n'
            'StudyOS bunu senin yerine planlayacak.',
      ),
      _TourCard(
        kind: _TourKind.blocksSpotlight,
        title: 'Günlük Çalışma Planı',
        spotlightLabel: 'Bugünkü bloklar',
        spotlightChips: todayBlocks.isEmpty
            ? const ['Konu', 'Tekrar', 'Mini quiz']
            : todayBlocks,
        body:
            'Bugünkü çalışma blokların burada bulunur.\n\n'
            'Konu çalışması, tekrar, mini quiz, deneme…\n'
            'Hepsi gün boyunca burada sıralanır.\n\n'
            'Tamamladıkça otomatik güncellenir.\n'
            'Senin $hoursLine göre ayarlandı.',
      ),
      _TourCard(
        kind: _TourKind.navSpotlight,
        title: 'Derslerim',
        spotlightLabel: 'Derslerim',
        navIndex: 1,
        body:
            'Burada bütün derslerini görebilirsin.\n\n'
            'Bir derse girdiğinde o derse ait tüm konular, ilerlemen, '
            'kaynakların, AI açıklamaları ve çalışma geçmişin tek yerde bulunur.\n\n'
            'Öncelikli güçlendirme: $weakLine.',
      ),
      _TourCard(
        kind: _TourKind.topicSurface,
        title: 'Konu Çalışma Alanı',
        spotlightLabel: 'Çalışma yüzeyi',
        body:
            'StudyOS’un merkezi burasıdır.\n\n'
            'Bir konuya girdiğinde çalışma, pomodoro, kaynak, AI açıklaması, '
            'mini quiz ve notlar aynı ekranda bulunur.\n\n'
            'Modüller arasında dolaşmana gerek kalmaz.',
      ),
      _TourCard(
        kind: _TourKind.navSpotlight,
        title: 'Günlük Deneme',
        spotlightLabel: 'Deneme',
        navIndex: -1,
        body:
            'StudyOS sana düzenli denemeler oluşturur.\n\n'
            'Sonuçlarını analiz eder.\n'
            'Hangi konularda geliştiğini, hangilerinde zorlandığını '
            'otomatik takip eder.',
      ),
      _TourCard(
        kind: _TourKind.navSpotlight,
        title: 'Yolculuğum',
        spotlightLabel: 'Yolculuk',
        navIndex: 3,
        body:
            'Burada uzun vadeli gelişimini takip edebilirsin.\n\n'
            'Sınava kalan gün, çalışma serin, gelişim trendlerin, '
            'istatistiklerin ve hedeflerin tek yerde bulunur.',
      ),
      _TourCard(
        kind: _TourKind.coach,
        title: 'AI Koçun',
        spotlightLabel: 'Koç',
        body:
            'StudyOS sadece program hazırlamaz.\n\n'
            'Çalışma alışkanlıklarını takip eder, zayıf yönlerini fark eder '
            've sana günlük öneriler sunar.\n\n'
            'Ancak çalışma kararlarını kanıtlara göre verir.',
      ),
      _TourCard(
        kind: _TourKind.profile,
        title: 'Profil',
        spotlightLabel: 'Profil',
        body:
            'Profil ekranında hedeflerini, alışkanlıklarını, '
            'AI’nın seni nasıl gördüğünü, tema ve uygulama ayarlarını '
            'yönetebilirsin.\n\n'
            'Bu turu istediğin zaman “StudyOS’u yeniden tanı” ile açabilirsin.',
      ),
      _TourCard(
        kind: _TourKind.finale,
        title: 'Artık hazırsın.',
        body:
            'Bugünkü ilk görevin seni bekliyor'
            '${nextTask == null || nextTask.isEmpty ? '.' : ':\n$taskLine'}\n\n'
            'Başarılar, $_name.\n'
            'Birlikte $goalLine hedefine ulaşacağız.',
        cta: 'Bugüne Başla',
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final dashState = ref.watch(dashboardProvider);
    final dash = dashState is DashboardLoaded ? dashState.dashboard : null;
    final planner = ref.watch(plannerProvider);

    final examRaw =
        profile?.activeExamType ?? profile?.primaryExamType ?? 'sınav';
    final examLabel = examRaw.toUpperCase();
    final target = profile?.examTargets.isNotEmpty == true
        ? profile!.examTargets.first
        : null;
    final branch = target?.branch;
    final examDate = target?.examDate ??
        dash?.journeyExamDate ??
        nextExamDate(examRaw);
    final daysLeft = dash?.journeyDaysRemaining ??
        examDate.difference(DateTime.now()).inDays;
    final dailyMinutes = profile?.dailyStudyMinutes;

    String? weakHint;
    final reason = profile?.baselineReason ?? '';
    if (reason.contains('Zayıf:')) {
      weakHint = reason.split('Zayıf:').last.split('·').first.trim();
    }
    weakHint ??= dash?.subjectsWeakest;

    final nextTask = dash?.nextAction?.title;

    final todayBlocks = <String>[];
    final draft = switch (planner) {
      PlannerAccepted(:final draft) => draft,
      PlannerPreview(:final draft) => draft,
      _ => null,
    };
    if (draft != null) {
      final now = DateTime.now();
      final today = DateTime(now.year, now.month, now.day);
      for (final item in draft.items) {
        final d = DateTime(
          item.studyDate.year,
          item.studyDate.month,
          item.studyDate.day,
        );
        if (d == today) {
          todayBlocks.add(item.subject);
          if (todayBlocks.length >= 3) break;
        }
      }
    }
    if (todayBlocks.isEmpty && draft != null && draft.items.isNotEmpty) {
      for (final item in draft.items.take(3)) {
        todayBlocks.add(item.subject);
      }
    }

    final cards = _buildCards(
      examLabel: examLabel,
      branch: branch,
      daysLeft: daysLeft,
      dailyMinutes: dailyMinutes,
      weakHint: weakHint,
      nextTask: nextTask,
      todayBlocks: todayBlocks,
    );
    final card = cards[_page.clamp(0, cards.length - 1)];
    final last = _page >= cards.length - 1;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Row(
                children: [
                  if (_page > 0)
                    IconButton(
                      onPressed: _back,
                      icon: const Icon(Icons.arrow_back),
                    )
                  else
                    const SizedBox(width: 48),
                  Expanded(
                    child: Text(
                      '${_page + 1} / ${cards.length}',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                  ),
                  TextButton(
                    onPressed: _finish,
                    child: const Text('Atla'),
                  ),
                ],
              ),
            ),
            Expanded(
              child: FadeTransition(
                opacity: CurvedAnimation(parent: _enter, curve: Curves.easeOut),
                child: ScaleTransition(
                  scale: Tween<double>(begin: 0.96, end: 1).animate(
                    CurvedAnimation(parent: _enter, curve: Curves.easeOutBack),
                  ),
                  child: _TourCardView(card: card),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
              child: FilledButton(
                onPressed: () => _next(cards.length),
                child: Text(card.cta ?? (last ? 'Bugüne Başla' : 'Devam')),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

enum _TourKind {
  welcome,
  todaySpotlight,
  blocksSpotlight,
  navSpotlight,
  topicSurface,
  coach,
  profile,
  finale,
}

class _TourCard {
  const _TourCard({
    required this.kind,
    required this.title,
    required this.body,
    this.cta,
    this.spotlightLabel,
    this.spotlightValue,
    this.spotlightChips,
    this.navIndex,
  });

  final _TourKind kind;
  final String title;
  final String body;
  final String? cta;
  final String? spotlightLabel;
  final String? spotlightValue;
  final List<String>? spotlightChips;
  final int? navIndex;
}

class _TourCardView extends StatelessWidget {
  const _TourCardView({required this.card});

  final _TourCard card;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (card.kind != _TourKind.welcome && card.kind != _TourKind.finale)
            Expanded(
              flex: 5,
              child: _SpotlightStage(card: card),
            )
          else
            Expanded(
              flex: 3,
              child: Center(
                child: Icon(
                  card.kind == _TourKind.finale
                      ? Icons.rocket_launch_outlined
                      : Icons.auto_awesome,
                  size: 64,
                  color: scheme.primary,
                ),
              ),
            ),
          const SizedBox(height: 16),
          Text(
            card.title,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 12),
          Expanded(
            flex: 4,
            child: SingleChildScrollView(
              child: Text(
                card.body,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      height: 1.45,
                    ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SpotlightStage extends StatelessWidget {
  const _SpotlightStage({required this.card});

  final _TourCard card;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Blurred faux app chrome
          ImageFiltered(
            imageFilter: ImageFilter.blur(sigmaX: 6, sigmaY: 6),
            child: Opacity(
              opacity: 0.55,
              child: Container(
                color: scheme.surfaceContainerHighest,
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Container(
                      height: 18,
                      width: 120,
                      decoration: BoxDecoration(
                        color: scheme.onSurface.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(6),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Expanded(
                      child: Container(
                        decoration: BoxDecoration(
                          color: scheme.onSurface.withValues(alpha: 0.06),
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: List.generate(
                        5,
                        (i) => Container(
                          width: 28,
                          height: 28,
                          decoration: BoxDecoration(
                            color: scheme.onSurface.withValues(alpha: 0.1),
                            shape: BoxShape.circle,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Spotlight card
          Align(
            alignment: Alignment.center,
            child: Transform.scale(
              scale: 1.04,
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 18),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: scheme.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: scheme.primary, width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: scheme.primary.withValues(alpha: 0.25),
                      blurRadius: 24,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: _spotlightContent(context),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _spotlightContent(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    switch (card.kind) {
      case _TourKind.todaySpotlight:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              card.spotlightLabel ?? 'Sıradaki İş',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: scheme.primary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              card.spotlightValue ?? 'İlk görev',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 10),
            FilledButton.tonal(
              onPressed: null,
              child: const Text('Başla'),
            ),
          ],
        );
      case _TourKind.blocksSpotlight:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              card.spotlightLabel ?? 'Bugünkü bloklar',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: scheme.primary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final c in card.spotlightChips ?? const <String>[])
                  Chip(label: Text(c)),
              ],
            ),
          ],
        );
      case _TourKind.navSpotlight:
        if (card.navIndex != null && card.navIndex! < 0) {
          return Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                card.spotlightLabel ?? 'Deneme',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: scheme.primary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 10),
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(Icons.quiz_outlined, color: scheme.primary),
                title: const Text('Günün Denemesi'),
                subtitle: const Text('Sonuçlar otomatik analiz edilir'),
              ),
            ],
          );
        }
        final labels = ['Bugün', 'Derslerim', 'Planım', 'Yolculuk', 'Profil'];
        final idx = card.navIndex ?? 1;
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              card.spotlightLabel ?? '',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: scheme.primary,
                  ),
            ),
            const SizedBox(height: 14),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                for (var i = 0; i < labels.length; i++)
                  Column(
                    children: [
                      Icon(
                        i == idx
                            ? Icons.radio_button_checked
                            : Icons.circle_outlined,
                        color: i == idx
                            ? scheme.primary
                            : scheme.onSurfaceVariant,
                        size: 22,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        labels[i],
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight:
                              i == idx ? FontWeight.w700 : FontWeight.w400,
                          color: i == idx
                              ? scheme.primary
                              : scheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ],
        );
      case _TourKind.topicSurface:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              card.spotlightLabel ?? 'Çalışma yüzeyi',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: scheme.primary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: const [
                Chip(label: Text('Pomodoro')),
                Chip(label: Text('Kaynak')),
                Chip(label: Text('AI')),
                Chip(label: Text('Quiz')),
                Chip(label: Text('Not')),
              ],
            ),
          ],
        );
      case _TourKind.coach:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AI Koç',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: scheme.primary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Bugün için net bir öneri · kanıta dayalı',
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ],
        );
      case _TourKind.profile:
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Profil',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: scheme.primary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            const Text('Hedef · Alışkanlık · Tema · Yeniden tanı'),
          ],
        );
      default:
        return const SizedBox.shrink();
    }
  }
}
