import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../features/auth/presentation/providers/auth_provider.dart';
import '../../../../features/auth/presentation/providers/auth_state.dart';
import '../providers/first_run_phase_provider.dart';
import '../providers/learning_profile_provider.dart';
import '../providers/onboarding_provider.dart';
import '../welcome/exam_subject_limits.dart';
import '../welcome/welcome_conversation_script.dart';

/// RC3 — Form yerine sabit soru + seçenek sohbeti.
/// Saat / net / ders netleri sürgü ile; eğitim durumu sınava göre filtrelenir.
class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _scroll = ScrollController();
  final _textCtrl = TextEditingController();
  final _answers = WelcomeAnswers();
  final List<_Line> _lines = [];
  late WelcomeConversationScript _script;
  WelcomeStep _step = WelcomeStep.intro;
  final Set<String> _multi = {};
  bool _saving = false;
  bool _questionReady = false;
  String? _error;

  double _hourValue = 2.5;
  double _scoreValue = 90;
  final Map<String, double> _subjectDraft = {};

  @override
  void initState() {
    super.initState();
    final auth = ref.read(authProvider);
    final name = switch (auth) {
      AuthAuthenticated(:final user) => user.firstName,
      _ => 'dostum',
    };
    _script = WelcomeConversationScript(firstName: name);
    WidgetsBinding.instance.addPostFrameCallback((_) => _pushQuestion());
  }

  @override
  void dispose() {
    _scroll.dispose();
    _textCtrl.dispose();
    super.dispose();
  }

  ChatBubble get _current => _script.bubbleFor(_step, _answers);

  void _resetSliderState(ChatBubble bubble) {
    if (bubble.mode == AnswerMode.hourSlider) {
      _hourValue = _answers.availableHours.clamp(bubble.sliderMin, bubble.sliderMax);
    } else if (bubble.mode == AnswerMode.scoreSlider) {
      _scoreValue = _answers.targetNet.clamp(bubble.sliderMin, bubble.sliderMax);
    } else if (bubble.mode == AnswerMode.subjectSliders) {
      _subjectDraft
        ..clear()
        ..addEntries(
          bubble.subjectLimits.map(
            (s) => MapEntry(
              s.id,
              (_answers.subjectNets[s.id] ?? (s.maxQuestions * 0.4))
                  .clamp(0, s.maxQuestions.toDouble()),
            ),
          ),
        );
    }
  }

  Future<void> _pushQuestion() async {
    final bubble = _current;
    if (bubble.text.isEmpty) return;

    setState(() {
      _questionReady = false;
      _multi.clear();
      _resetSliderState(bubble);
      _lines.add(_Line.ai(bubble.text));
    });
    _scrollBottom();

    await Future<void>.delayed(const Duration(milliseconds: 220));
    if (!mounted) return;
    setState(() => _questionReady = true);
    _scrollBottom();
  }

  void _scrollBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scroll.hasClients) return;
      _scroll.animateTo(
        _scroll.position.maxScrollExtent + 160,
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOut,
      );
    });
  }

  Future<void> _applyChoice(String id, String label) async {
    if (_saving || !_questionReady) return;
    final bubble = _current;

    if (bubble.multiSelect || bubble.mode == AnswerMode.multiSelect) {
      setState(() {
        if (_multi.contains(id)) {
          _multi.remove(id);
        } else {
          _multi.add(id);
        }
      });
      return;
    }

    setState(() {
      _questionReady = false;
      _lines.add(_Line.user(label));
    });
    _applyAnswer(id, label);
    await _advance();
  }

  Future<void> _confirmMulti() async {
    if (_multi.isEmpty || _saving || !_questionReady) return;
    final labels = _multi.toList();
    setState(() {
      _questionReady = false;
      _lines.add(_Line.user(labels.join(', ')));
    });
    if (_step == WelcomeStep.strongSubjects) {
      _answers.strongSubjects = labels;
    } else if (_step == WelcomeStep.weakSubjects) {
      _answers.weakSubjects = labels;
    }
    await _advance();
  }

  Future<void> _confirmHourSlider() async {
    if (_saving || !_questionReady) return;
    final hours = _hourValue;
    final mins = (hours * 60).round();
    final label = hours == hours.roundToDouble()
        ? '${hours.toInt()} saat / gün'
        : '${hours.toStringAsFixed(1)} saat / gün';
    setState(() {
      _questionReady = false;
      _lines.add(_Line.user(label));
      _answers.availableHours = hours;
      _answers.dailyMinutes = mins;
    });
    await _advance();
  }

  Future<void> _confirmScoreSlider() async {
    if (_saving || !_questionReady) return;
    final limits = scoreLimitsFor(_answers.examType, _answers.branch);
    final v = _scoreValue.roundToDouble();
    setState(() {
      _questionReady = false;
      _lines.add(_Line.user('${v.toStringAsFixed(0)} ${limits.scoreWord}'));
      _answers.targetNet = v;
    });
    await _advance();
  }

  Future<void> _confirmSubjectSliders() async {
    if (_saving || !_questionReady) return;
    final nets = Map<String, double>.from(_subjectDraft);
    final summary = nets.entries
        .map((e) => '${e.key} ${e.value.toStringAsFixed(0)}')
        .join(', ');
    setState(() {
      _questionReady = false;
      _lines.add(_Line.user(summary.isEmpty ? 'Ders netleri kaydedildi' : summary));
      _answers.subjectNets = nets;
    });
    await _advance();
  }

  Future<void> _submitFreeText() async {
    final raw = _textCtrl.text.trim();
    if (raw.isEmpty || _saving || !_questionReady) return;
    setState(() {
      _questionReady = false;
      _lines.add(_Line.user(raw));
      _textCtrl.clear();
    });
    if (_step == WelcomeStep.anythingElse) {
      _answers.anythingElse = raw;
    }
    await _advance();
  }

  void _applyAnswer(String id, String label) {
    switch (_step) {
      case WelcomeStep.intro:
        break;
      case WelcomeStep.exam:
        _answers.examType = id;
        // Sınav değişince hedefi o sınavın ortasına çek
        final lim = scoreLimitsFor(id, _answers.branch);
        _answers.targetNet = ((lim.targetMin + lim.targetMax) / 2).roundToDouble();
        break;
      case WelcomeStep.branch:
        _answers.branch = id;
        break;
      case WelcomeStep.education:
        _answers.education = label;
        break;
      case WelcomeStep.subjectNets:
        if (id == 'skip_nets') _answers.subjectNets = {};
        break;
      case WelcomeStep.studiedBefore:
        _answers.studiedBefore = id == 'yes';
        break;
      case WelcomeStep.habit:
        _answers.habit = label;
        break;
      case WelcomeStep.studyStyle:
        _answers.studyStyle = label;
        break;
      case WelcomeStep.anythingElse:
        if (id == 'skip_extra') _answers.anythingElse = null;
        break;
      case WelcomeStep.dailyTime:
      case WelcomeStep.targetNet:
      case WelcomeStep.strongSubjects:
      case WelcomeStep.weakSubjects:
      case WelcomeStep.summary:
      case WelcomeStep.done:
        break;
    }
  }

  Future<void> _advance() async {
    final next = _script.nextAfter(_step, _answers);
    if (next == WelcomeStep.done || _step == WelcomeStep.summary) {
      await _finish();
      return;
    }
    setState(() => _step = next);
    await Future<void>.delayed(const Duration(milliseconds: 200));
    if (!mounted) return;
    await _pushQuestion();
  }

  Future<void> _finish() async {
    setState(() {
      _saving = true;
      _error = null;
      _questionReady = false;
    });
    try {
      await ref
          .read(onboardingProvider.notifier)
          .complete(_answers.toOnboardingPayload());
      await ref.read(firstRunPhaseProvider.notifier).setPhase('calibration');
      invalidateLearningProfile(ref);
      if (!mounted) return;
      context.go('/setup/calibration');
    } on AppException catch (e) {
      setState(() => _error = e.message);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final bubble = _current;
    final showChoices =
        !_saving && _questionReady && _step != WelcomeStep.done;

    return Scaffold(
      backgroundColor: scheme.surface,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 8),
              child: Row(
                children: [
                  Icon(Icons.chat_bubble_outline, color: scheme.primary, size: 22),
                  const SizedBox(width: 8),
                  Text(
                    'Seni tanıyalım',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                controller: _scroll,
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                itemCount: _lines.length,
                itemBuilder: (_, i) {
                  final line = _lines[i];
                  return Align(
                    alignment: line.fromAi
                        ? Alignment.centerLeft
                        : Alignment.centerRight,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 12,
                      ),
                      constraints: BoxConstraints(
                        maxWidth: MediaQuery.sizeOf(context).width * 0.86,
                      ),
                      decoration: BoxDecoration(
                        color: line.fromAi
                            ? scheme.surfaceContainerHighest
                            : scheme.primary,
                        borderRadius: BorderRadius.only(
                          topLeft: const Radius.circular(16),
                          topRight: const Radius.circular(16),
                          bottomLeft: Radius.circular(line.fromAi ? 4 : 16),
                          bottomRight: Radius.circular(line.fromAi ? 16 : 4),
                        ),
                      ),
                      child: Text(
                        line.text,
                        style: TextStyle(
                          color: line.fromAi
                              ? scheme.onSurface
                              : scheme.onPrimary,
                          height: 1.4,
                          fontWeight:
                              line.fromAi ? FontWeight.w500 : FontWeight.w400,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  _error!,
                  style: TextStyle(color: scheme.error),
                ),
              ),
            if (_saving)
              const Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  children: [
                    LinearProgressIndicator(),
                    SizedBox(height: 8),
                    Text('Profilin hazırlanıyor…'),
                  ],
                ),
              )
            else if (showChoices)
              _AnswerPanel(
                bubble: bubble,
                multiSelected: _multi,
                textCtrl: _textCtrl,
                hourValue: _hourValue,
                scoreValue: _scoreValue,
                subjectDraft: _subjectDraft,
                onHourChanged: (v) => setState(() => _hourValue = v),
                onScoreChanged: (v) => setState(() => _scoreValue = v),
                onSubjectChanged: (id, v) =>
                    setState(() => _subjectDraft[id] = v),
                onChoice: _applyChoice,
                onConfirmMulti: _confirmMulti,
                onSubmitFreeText: _submitFreeText,
                onConfirmHour: _confirmHourSlider,
                onConfirmScore: _confirmScoreSlider,
                onConfirmSubjects: _confirmSubjectSliders,
              ),
          ],
        ),
      ),
    );
  }
}

class _AnswerPanel extends StatelessWidget {
  const _AnswerPanel({
    required this.bubble,
    required this.multiSelected,
    required this.textCtrl,
    required this.hourValue,
    required this.scoreValue,
    required this.subjectDraft,
    required this.onHourChanged,
    required this.onScoreChanged,
    required this.onSubjectChanged,
    required this.onChoice,
    required this.onConfirmMulti,
    required this.onSubmitFreeText,
    required this.onConfirmHour,
    required this.onConfirmScore,
    required this.onConfirmSubjects,
  });

  final ChatBubble bubble;
  final Set<String> multiSelected;
  final TextEditingController textCtrl;
  final double hourValue;
  final double scoreValue;
  final Map<String, double> subjectDraft;
  final ValueChanged<double> onHourChanged;
  final ValueChanged<double> onScoreChanged;
  final void Function(String id, double value) onSubjectChanged;
  final Future<void> Function(String id, String label) onChoice;
  final Future<void> Function() onConfirmMulti;
  final Future<void> Function() onSubmitFreeText;
  final Future<void> Function() onConfirmHour;
  final Future<void> Function() onConfirmScore;
  final Future<void> Function() onConfirmSubjects;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final hint = switch (bubble.mode) {
      AnswerMode.hourSlider ||
      AnswerMode.scoreSlider ||
      AnswerMode.subjectSliders =>
        'Sürgüyü ayarla, sonra onayla',
      AnswerMode.multiSelect => 'Birden fazla seç, sonra Devam’a bas',
      _ => 'Cevabını seç',
    };

    return Material(
      elevation: 6,
      color: scheme.surface,
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                hint,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: scheme.onSurfaceVariant,
                    ),
              ),
              const SizedBox(height: 10),
              if (bubble.mode == AnswerMode.hourSlider) ...[
                _SliderBlock(
                  valueLabel: hourValue == hourValue.roundToDouble()
                      ? '${hourValue.toInt()} saat'
                      : '${hourValue.toStringAsFixed(1)} saat',
                  value: hourValue,
                  min: bubble.sliderMin,
                  max: bubble.sliderMax,
                  divisions: bubble.sliderDivisions,
                  onChanged: onHourChanged,
                ),
                FilledButton(
                  onPressed: onConfirmHour,
                  child: const Text('Onayla'),
                ),
              ] else if (bubble.mode == AnswerMode.scoreSlider) ...[
                _SliderBlock(
                  valueLabel:
                      '${scoreValue.round()} ${bubble.sliderUnit}'.trim(),
                  value: scoreValue,
                  min: bubble.sliderMin,
                  max: bubble.sliderMax,
                  divisions: bubble.sliderDivisions,
                  onChanged: onScoreChanged,
                ),
                FilledButton(
                  onPressed: onConfirmScore,
                  child: const Text('Onayla'),
                ),
              ] else if (bubble.mode == AnswerMode.subjectSliders) ...[
                ConstrainedBox(
                  constraints: BoxConstraints(
                    maxHeight: MediaQuery.sizeOf(context).height * 0.38,
                  ),
                  child: ListView(
                    shrinkWrap: true,
                    children: [
                      for (final s in bubble.subjectLimits)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: _SliderBlock(
                            valueLabel:
                                '${s.label}: ${(subjectDraft[s.id] ?? 0).round()} / ${s.maxQuestions}',
                            value: (subjectDraft[s.id] ?? 0)
                                .clamp(0, s.maxQuestions.toDouble()),
                            min: 0,
                            max: s.maxQuestions.toDouble(),
                            divisions: s.maxQuestions,
                            onChanged: (v) => onSubjectChanged(s.id, v),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                FilledButton(
                  onPressed: onConfirmSubjects,
                  child: const Text('Ders netlerini kaydet'),
                ),
                const SizedBox(height: 8),
                for (final c in bubble.choices)
                  OutlinedButton(
                    onPressed: () => onChoice(c.id, c.label),
                    child: Text(c.label),
                  ),
              ] else ...[
                if (bubble.freeTextHint != null) ...[
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: textCtrl,
                          keyboardType: bubble.numeric
                              ? TextInputType.number
                              : TextInputType.text,
                          decoration: InputDecoration(
                            hintText: bubble.freeTextHint,
                            border: const OutlineInputBorder(),
                            isDense: true,
                          ),
                          onSubmitted: (_) => onSubmitFreeText(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton.filled(
                        onPressed: onSubmitFreeText,
                        icon: const Icon(Icons.send_rounded),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                ],
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final c in bubble.choices)
                      if (bubble.multiSelect ||
                          bubble.mode == AnswerMode.multiSelect)
                        FilterChip(
                          selected: multiSelected.contains(c.id),
                          label: Text(c.label),
                          onSelected: (_) => onChoice(c.id, c.label),
                        )
                      else
                        OutlinedButton(
                          onPressed: () => onChoice(c.id, c.label),
                          child: Text(c.label),
                        ),
                    if (bubble.multiSelect ||
                        bubble.mode == AnswerMode.multiSelect)
                      FilledButton(
                        onPressed:
                            multiSelected.isEmpty ? null : onConfirmMulti,
                        child: const Text('Devam'),
                      ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _SliderBlock extends StatelessWidget {
  const _SliderBlock({
    required this.valueLabel,
    required this.value,
    required this.min,
    required this.max,
    required this.onChanged,
    this.divisions,
  });

  final String valueLabel;
  final double value;
  final double min;
  final double max;
  final int? divisions;
  final ValueChanged<double> onChanged;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          valueLabel,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                color: scheme.primary,
              ),
        ),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: divisions,
          label: valueLabel,
          onChanged: onChanged,
        ),
      ],
    );
  }
}

class _Line {
  const _Line._(this.fromAi, this.text);
  factory _Line.ai(String text) => _Line._(true, text);
  factory _Line.user(String text) => _Line._(false, text);
  final bool fromAi;
  final String text;
}
