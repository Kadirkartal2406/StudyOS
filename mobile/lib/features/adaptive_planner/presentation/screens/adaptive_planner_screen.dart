import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../onboarding/domain/entities/learning_profile_entity.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../subjects/presentation/widgets/subject_code_chip.dart';
import '../../domain/entities/planner_entity.dart';
import '../providers/planner_provider.dart';

const _dayLabels = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];

/// Alignment Sprint-4 — Suggest→Accept yüzeyi (plan kurucu wizard değil).
/// Profil doluysa parametre adımları atlanır; generate aynı API.
class AdaptivePlannerScreen extends ConsumerStatefulWidget {
  const AdaptivePlannerScreen({super.key, this.subjectCode});

  final String? subjectCode;

  @override
  ConsumerState<AdaptivePlannerScreen> createState() =>
      _AdaptivePlannerScreenState();
}

class _AdaptivePlannerScreenState extends ConsumerState<AdaptivePlannerScreen> {
  int _step = 0;
  String? _exam;
  final _netCtrl = TextEditingController(text: '90');
  final _hoursCtrl = TextEditingController(text: '2');
  final _selectedDays = <int>{0, 2, 4};
  bool _defaultsApplied = false;
  bool _profileReady = false;

  @override
  void dispose() {
    _netCtrl.dispose();
    _hoursCtrl.dispose();
    super.dispose();
  }

  bool _isProfileReady(LearningProfileEntity? profile) {
    if (profile == null) return false;
    final exam = profile.activeExamType ?? profile.resolvedPrimaryExamType;
    if (exam == null || exam.isEmpty) return false;
    if (profile.availableDays.isEmpty) return false;
    if (profile.availableHours <= 0) return false;
    final hasNet = profile.examTargets.any((t) => t.targetNet != null);
    return hasNet;
  }

  Future<void> _generate() async {
    final exam = _exam ?? 'tyt';
    final net = double.tryParse(_netCtrl.text.replaceAll(',', '.')) ?? 90;
    final hours = double.tryParse(_hoursCtrl.text.replaceAll(',', '.')) ?? 2;
    await ref.read(plannerProvider.notifier).generate(
          targetExam: exam,
          targetNet: net,
          availableDays: _selectedDays.toList()..sort(),
          availableHours: hours,
        );
    setState(() => _step = 4);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(plannerProvider);
    final profile = ref.watch(learningProfileProvider).valueOrNull;
    final examTypes = profile?.allowedExamTypes ??
        const [
          'tyt',
          'ayt',
          'yks',
          'lgs',
          'kpss',
          'ales',
          'dgs',
          'yds',
          'custom',
        ];

    if (!_defaultsApplied && profile != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted || _defaultsApplied) return;
        setState(() {
          _exam = profile.activeExamType ??
              profile.resolvedPrimaryExamType ??
              examTypes.first;
          if (profile.availableDays.isNotEmpty) {
            _selectedDays
              ..clear()
              ..addAll(profile.availableDays);
          }
          _hoursCtrl.text = profile.availableHours.toString();
          final activeCode = profile.activeExamType;
          final activeTargets = activeCode == null
              ? <ExamTargetEntity>[]
              : profile.examTargets
                  .where((e) => e.examType == activeCode)
                  .toList();
          final primary = profile.examTargets.where((e) => e.isPrimary);
          final net = activeTargets.isNotEmpty
              ? activeTargets.first.targetNet
              : (primary.isNotEmpty
                  ? primary.first.targetNet
                  : (profile.examTargets.isNotEmpty
                      ? profile.examTargets.first.targetNet
                      : null));
          if (net != null) _netCtrl.text = net.toStringAsFixed(0);
          _profileReady = _isProfileReady(profile);
          _defaultsApplied = true;
        });
      });
    }

    final exam = _exam ?? examTypes.first;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Akıllı Çalışma Önerisi'),
        actions: [
          if (widget.subjectCode != null && widget.subjectCode!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: SubjectCodeChip(subjectCode: widget.subjectCode!),
            ),
          if (!_profileReady && _step > 0 && state is! PlannerLoading)
            TextButton(
              onPressed: () {
                if (_step == 4) {
                  ref.read(plannerProvider.notifier).reset();
                }
                setState(() => _step = (_step - 1).clamp(0, 4));
              },
              child: const Text('Geri'),
            ),
        ],
      ),
      body: switch (state) {
        PlannerLoading() => const Center(child: CircularProgressIndicator()),
        PlannerError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                FilledButton(
                  onPressed: () {
                    ref.read(plannerProvider.notifier).reset();
                    setState(() => _step = 0);
                  },
                  child: const Text('Başa dön'),
                ),
              ],
            ),
          ),
        PlannerAccepted(:final draft) => _AcceptedView(draftId: draft.id),
        PlannerPreview(:final draft, :final explanation, :final errorMessage) =>
          _PreviewView(
            draft: draft,
            explanation: explanation,
            errorMessage: errorMessage,
            onExplain: () => ref.read(plannerProvider.notifier).explain(),
            onAccept: () => ref.read(plannerProvider.notifier).accept(),
            onForceAccept: () =>
                ref.read(plannerProvider.notifier).accept(force: true),
            onReject: () {
              ref.read(plannerProvider.notifier).reset();
              setState(() => _step = 0);
            },
          ),
        _ when _profileReady => _SuggestReadyView(
            exam: exam,
            netText: _netCtrl.text,
            days: _selectedDays.map((d) => _dayLabels[d]).join(', '),
            hoursText: _hoursCtrl.text,
            onShowSuggestion: _generate,
            onEditParams: () => setState(() => _profileReady = false),
          ),
        _ => _WizardBody(
            step: _step,
            exam: exam,
            examTypes: examTypes,
            netCtrl: _netCtrl,
            hoursCtrl: _hoursCtrl,
            selectedDays: _selectedDays,
            onExam: (v) => setState(() => _exam = v),
            onToggleDay: (d) => setState(() {
              if (_selectedDays.contains(d)) {
                if (_selectedDays.length > 1) _selectedDays.remove(d);
              } else {
                _selectedDays.add(d);
              }
            }),
            onNext: () {
              if (_step < 3) {
                setState(() => _step++);
              } else {
                _generate();
              }
            },
          ),
      },
    );
  }
}

/// Profil dolu — parametre sormadan öneri üret.
class _SuggestReadyView extends StatelessWidget {
  const _SuggestReadyView({
    required this.exam,
    required this.netText,
    required this.days,
    required this.hoursText,
    required this.onShowSuggestion,
    required this.onEditParams,
  });

  final String exam;
  final String netText;
  final String days;
  final String hoursText;
  final VoidCallback onShowSuggestion;
  final VoidCallback onEditParams;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Sana Özel Plan Hazır',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 8),
        Text(
          'StudyOS mevcut durumunu, hedeflerini ve geçmiş verilerini analiz etti. Aşağıdaki ayarlara göre senin için en verimli planı oluşturacak.',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Sınav: ${exam.toUpperCase()}'),
                Text('Hedef net: $netText'),
                Text('Günler: $days'),
                Text('Saat / gün: $hoursText'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),
        FilledButton(
          onPressed: onShowSuggestion,
          child: const Text('Öneriyi göster'),
        ),
        TextButton(
          onPressed: onEditParams,
          child: const Text('Parametreleri düzenle (Gelişmiş)'),
        ),
      ],
    );
  }
}

class _WizardBody extends StatelessWidget {
  const _WizardBody({
    required this.step,
    required this.exam,
    required this.examTypes,
    required this.netCtrl,
    required this.hoursCtrl,
    required this.selectedDays,
    required this.onExam,
    required this.onToggleDay,
    required this.onNext,
  });

  final int step;
  final String exam;
  final List<String> examTypes;
  final TextEditingController netCtrl;
  final TextEditingController hoursCtrl;
  final Set<int> selectedDays;
  final ValueChanged<String> onExam;
  final ValueChanged<int> onToggleDay;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Profil bilgisi eksik · Adım ${step + 1} / 4',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Text(
          'Öneri için gereken bilgiler. Bu bir plan kurma sihirbazı değil.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 16),
        if (step == 0) ...[
          const Text('Hedef sınav ve net'),
          DropdownButtonFormField<String>(
            // ignore: deprecated_member_use
            value: examTypes.contains(exam) ? exam : examTypes.first,
            items: [
              for (final t in examTypes)
                DropdownMenuItem(value: t, child: Text(t.toUpperCase())),
            ],
            onChanged: (v) => onExam(v ?? examTypes.first),
          ),
          TextField(
            controller: netCtrl,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Hedef net'),
          ),
        ] else if (step == 1) ...[
          const Text('Boş günlerini seç'),
          Wrap(
            spacing: 8,
            children: [
              for (var i = 0; i < 7; i++)
                FilterChip(
                  label: Text(_dayLabels[i]),
                  selected: selectedDays.contains(i),
                  onSelected: (_) => onToggleDay(i),
                ),
            ],
          ),
        ] else if (step == 2) ...[
          const Text('Günlük kullanılabilir saat'),
          TextField(
            controller: hoursCtrl,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Saat / gün'),
          ),
        ] else ...[
          const Text('Öneriyi oluşturmaya hazır.'),
          Text('Sınav: ${exam.toUpperCase()} · Net: ${netCtrl.text}'),
          Text('Günler: ${selectedDays.map((d) => _dayLabels[d]).join(', ')}'),
          Text('Saat: ${hoursCtrl.text}'),
        ],
        const SizedBox(height: 24),
        FilledButton(
          onPressed: onNext,
          child: Text(step < 3 ? 'İleri' : 'Öneriyi göster'),
        ),
      ],
    );
  }
}

class _PreviewView extends StatelessWidget {
  const _PreviewView({
    required this.draft,
    required this.onExplain,
    required this.onAccept,
    required this.onForceAccept,
    required this.onReject,
    this.explanation,
    this.errorMessage,
  });

  final PlannerDraftEntity draft;
  final String? explanation;
  final String? errorMessage;
  final VoidCallback onExplain;
  final Future<bool> Function() onAccept;
  final Future<bool> Function() onForceAccept;
  final VoidCallback onReject;

  Map<DateTime, List<PlannerItemEntity>> _groupByDay() {
    final map = <DateTime, List<PlannerItemEntity>>{};
    for (final item in draft.items) {
      final d = DateTime(
        item.studyDate.year,
        item.studyDate.month,
        item.studyDate.day,
      );
      map.putIfAbsent(d, () => []).add(item);
    }
    final keys = map.keys.toList()..sort();
    return {for (final k in keys) k: map[k]!};
  }

  String _dayLabel(DateTime d) {
    const names = [
      'Pazartesi',
      'Salı',
      'Çarşamba',
      'Perşembe',
      'Cuma',
      'Cumartesi',
      'Pazar',
    ];
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final label = names[d.weekday - 1];
    final dateStr = DateFormat('dd.MM').format(d);
    if (d == today) return 'Bugün · $dateStr';
    if (d == today.add(const Duration(days: 1))) return 'Yarın · $dateStr';
    return '$label · $dateStr';
  }

  @override
  Widget build(BuildContext context) {
    final byDay = _groupByDay();
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          draft.overviewReason ?? 'İşte çalışma planın',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          '${draft.targetExam.toUpperCase()} · hedef ~${draft.targetNet.toStringAsFixed(0)} · '
          'günde ~${draft.availableHours.toStringAsFixed(1)} saat',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 4),
        Text(
          'Onayladığında bu bloklar çalışma planına işlenir. Beğenmezsen düzenleyebilirsin.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        if (errorMessage != null) ...[
          const SizedBox(height: 8),
          Text(
            errorMessage!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
          TextButton(
            onPressed: () => onForceAccept(),
            child: const Text('Yine de ekle'),
          ),
        ],
        const SizedBox(height: 12),
        if (byDay.isEmpty)
          const Text('Plan maddesi yok — tekrar dene.')
        else
          for (final entry in byDay.entries)
            Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _dayLabel(entry.key),
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 8),
                    for (final item in entry.value) ...[
                      Text(
                        [
                          if (item.startTime != null && item.endTime != null)
                            '${item.startTime}–${item.endTime}',
                          item.subject,
                          if (item.topic != null && item.topic!.isNotEmpty)
                            item.topic!,
                        ].join(' · '),
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                      Text(
                        '${item.estimatedMinutes} dk'
                        '${item.targetQuestionCount > 0 ? ' · ${item.targetQuestionCount} soru' : ''}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      if (item.reason.isNotEmpty)
                        Text(
                          item.reason,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Theme.of(context)
                                    .colorScheme
                                    .onSurfaceVariant,
                              ),
                        ),
                      if (item != entry.value.last) const SizedBox(height: 10),
                    ],
                  ],
                ),
              ),
            ),
        const SizedBox(height: 8),
        if (explanation != null) ...[
          Text(
            'Neden bu öneri?',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          Text(explanation!),
          const SizedBox(height: 12),
        ],
        OutlinedButton(
          onPressed: onExplain,
          child: const Text('Bu planın mantığı'),
        ),
        const SizedBox(height: 8),
        FilledButton(
          onPressed: () async {
            final ok = await onAccept();
            if (ok && context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Plan onaylandı ve kaydedildi.'),
                ),
              );
            }
          },
          child: const Text('Planı Onayla'),
        ),
        TextButton(
          onPressed: onReject,
          child: const Text('Yeniden öner'),
        ),
      ],
    );
  }
}

class _AcceptedView extends StatelessWidget {
  const _AcceptedView({required this.draftId});

  final String draftId;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.check_circle, size: 56),
            const SizedBox(height: 12),
            const Text(
              'Harika! Bugünkü planın onaylandı. StudyOS ilerlemeni takip edecek.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => context.go('/study-plan'),
              child: const Text('Plana Git'),
            ),
            TextButton(
              onPressed: () => context.go('/dashboard'),
              child: const Text("Today'e git"),
            ),
          ],
        ),
      ),
    );
  }
}
