/// RC3 M24.1 + UX polish — İlk kullanım sohbet adımları.
library;

import 'exam_calendar.dart';
import 'exam_subject_limits.dart';

enum WelcomeStep {
  intro,
  exam,
  branch,
  education,
  dailyTime,
  targetNet,
  subjectNets,
  strongSubjects,
  weakSubjects,
  studiedBefore,
  habit,
  studyStyle,
  anythingElse,
  summary,
  done,
}

enum AnswerMode {
  choices,
  multiSelect,
  freeText,
  hourSlider,
  scoreSlider,
  subjectSliders,
}

class WelcomeAnswers {
  String? examType;
  String? branch;
  String? education;
  double availableHours = 2.5;
  int dailyMinutes = 150;
  Set<int> availableDays = {0, 1, 2, 3, 4};
  double targetNet = 90;
  /// Ders adı → ortalama net
  Map<String, double> subjectNets = {};
  List<String> strongSubjects = [];
  List<String> weakSubjects = [];
  bool? studiedBefore;
  String? habit;
  String? studyStyle;
  String? anythingElse;
  String? university;
  String? department;

  Map<String, dynamic> toOnboardingPayload() {
    final exam = examType ?? 'kpss';
    final examDate = nextExamDate(exam);
    final target = <String, dynamic>{
      'exam_type': exam,
      'is_primary': true,
      'target_net': targetNet,
      'exam_date': formatExamDateIso(examDate),
    };
    if (branch != null && branch!.isNotEmpty) {
      target['branch'] = branch;
    }
    if (university != null && university!.isNotEmpty) {
      target['target_university'] = university;
    }
    if (department != null && department!.isNotEmpty) {
      target['target_department'] = department;
    }

    final strong = strongSubjects.isEmpty
        ? null
        : 'Güçlü: ${strongSubjects.join(", ")}';
    final weak =
        weakSubjects.isEmpty ? null : 'Zayıf: ${weakSubjects.join(", ")}';
    final habitLine = habit == null ? null : 'Alışkanlık: $habit';
    final styleLine = studyStyle == null ? null : 'Tercih: $studyStyle';
    final before = studiedBefore == null
        ? null
        : (studiedBefore! ? 'Daha önce çalıştı' : 'Yeni başlıyor');
    final edu = education == null ? null : 'Eğitim: $education';
    final netsLine = subjectNets.isEmpty
        ? null
        : 'Ders netleri: ${subjectNets.entries.map((e) => '${e.key}=${e.value.toStringAsFixed(0)}').join('; ')}';
    final extra = (anythingElse == null || anythingElse!.trim().isEmpty)
        ? null
        : 'Ek not: ${anythingElse!.trim()}';

    final reasonParts = [
      edu,
      before,
      netsLine,
      strong,
      weak,
      habitLine,
      styleLine,
      extra,
    ].whereType<String>().toList();

    return {
      'exam_targets': [target],
      'available_days': availableDays.toList()..sort(),
      'available_hours': availableHours,
      'daily_study_minutes': dailyMinutes,
      'baseline_level': 'unknown',
      'baseline_reason': reasonParts.isEmpty
          ? 'Sohbet onboarding — seviye testinde netleşecek'
          : reasonParts.join(' · '),
    };
  }
}

class ChatBubble {
  const ChatBubble({
    required this.fromAi,
    required this.text,
    this.choices = const [],
    this.multiSelect = false,
    this.freeTextHint,
    this.numeric = false,
    this.mode = AnswerMode.choices,
    this.sliderMin = 0,
    this.sliderMax = 100,
    this.sliderDivisions,
    this.sliderUnit = '',
    this.subjectLimits = const [],
  });

  final bool fromAi;
  final String text;
  final List<ChatChoice> choices;
  final bool multiSelect;
  final String? freeTextHint;
  final bool numeric;
  final AnswerMode mode;
  final double sliderMin;
  final double sliderMax;
  final int? sliderDivisions;
  final String sliderUnit;
  final List<SubjectNetLimit> subjectLimits;
}

class ChatChoice {
  const ChatChoice({required this.id, required this.label});
  final String id;
  final String label;
}

class WelcomeConversationScript {
  WelcomeConversationScript({required this.firstName});

  final String firstName;

  bool needsYksBranch(String? exam) =>
      exam == 'yks' || exam == 'ayt' || exam == 'tyt';
  bool needsKpssBranch(String? exam) => exam == 'kpss' || exam == 'ags';

  String _examLabel(String? exam) => (exam ?? 'sınav').toUpperCase();

  ChatBubble bubbleFor(WelcomeStep step, WelcomeAnswers a) {
    final examL = _examLabel(a.examType);
    final limits = scoreLimitsFor(a.examType, a.branch);
    final scoreW = limits.scoreWord;
    switch (step) {
      case WelcomeStep.intro:
        return ChatBubble(
          fromAi: true,
          text:
              'Merhaba $firstName.\n\n'
              'StudyOS, sana özel çalışma planını bu kısa tanışma '
              'üzerine kurar.\n\n'
              'Sorduğum her soru günlük süre, hedef ve öncelikli dersleri '
              'doğru ayarlamak için kullanılır — yaklaşık 2 dakika sürer.',
          choices: const [
            ChatChoice(id: 'ready', label: 'Başlayalım'),
          ],
        );
      case WelcomeStep.exam:
        return const ChatBubble(
          fromAi: true,
          text:
              'Hangi sınava hazırlanıyorsun?\n\n'
              'Plan, konu dağılımı ve seviye testi buna göre şekillenir.',
          choices: [
            ChatChoice(id: 'kpss', label: 'KPSS'),
            ChatChoice(id: 'yks', label: 'YKS (TYT+AYT)'),
            ChatChoice(id: 'tyt', label: 'Sadece TYT'),
            ChatChoice(id: 'ayt', label: 'Sadece AYT'),
            ChatChoice(id: 'lgs', label: 'LGS'),
            ChatChoice(id: 'ales', label: 'ALES'),
            ChatChoice(id: 'yds', label: 'YDS'),
            ChatChoice(id: 'dgs', label: 'DGS'),
            ChatChoice(id: 'ags', label: 'AGS'),
          ],
        );
      case WelcomeStep.branch:
        if (needsYksBranch(a.examType)) {
          return const ChatBubble(
            fromAi: true,
            text:
                'YKS’de hangi alandan giriyorsun?\n\n'
                'AYT dersleri ve ağırlıklar buna göre seçilir.',
            choices: [
              ChatChoice(id: 'sayisal', label: 'Sayısal'),
              ChatChoice(id: 'ea', label: 'Eşit Ağırlık'),
              ChatChoice(id: 'sozel', label: 'Sözel'),
              ChatChoice(id: 'dil', label: 'Dil'),
            ],
          );
        }
        return ChatBubble(
          fromAi: true,
          text:
              '$examL’de hangi düzeyden gireceksin?\n\n'
              'Soru kapsamı ve genel kültür ağırlığı buna bağlıdır.',
          choices: const [
            ChatChoice(id: 'lisans', label: 'Lisans (A grubu)'),
            ChatChoice(id: 'onlisans', label: 'Önlisans'),
            ChatChoice(id: 'ortaogretim', label: 'Ortaöğretim'),
          ],
        );
      case WelcomeStep.education:
        final edu = educationChoicesFor(a.examType);
        return ChatBubble(
          fromAi: true,
          text:
              'Şu anki durumun nedir?\n\n'
              'Bu bilgi, tempo ve haftalık plan yoğunluğunu ayarlamak için '
              'kullanılır (ör. LGS için ortaokul, ALES için lisans sonrası).',
          choices: [
            for (final c in edu) ChatChoice(id: c.id, label: c.label),
          ],
        );
      case WelcomeStep.dailyTime:
        return ChatBubble(
          fromAi: true,
          text:
              '$examL için günde ortalama kaç saat ayırabilirsin?\n\n'
              'Bu süre, günlük çalışma bloklarının uzunluğunu belirler. '
              'Gerçekçi bir değer seç — plan buna kilitlenir.',
          mode: AnswerMode.hourSlider,
          sliderMin: 0.5,
          sliderMax: 8,
          sliderDivisions: 15,
          sliderUnit: 'saat',
        );
      case WelcomeStep.targetNet:
        return ChatBubble(
          fromAi: true,
          text:
              '$examL için hedef $scoreW’in nedir?\n\n'
              'Hedef, deneme temposu ve zorluk bandını etkiler. '
              'Sürgüyü kaydırarak seç.',
          mode: AnswerMode.scoreSlider,
          sliderMin: limits.targetMin,
          sliderMax: limits.targetMax,
          sliderDivisions: limits.targetDivisions,
          sliderUnit: scoreW,
        );
      case WelcomeStep.subjectNets:
        final subjects = subjectLimitsFor(a.examType, a.branch);
        return ChatBubble(
          fromAi: true,
          text:
              'Ders ders ortalama $scoreW’lerin nedir?\n\n'
              'Her ders için sürgü, o dersteki resmi soru sayısına kadar '
              'gidebilir (ör. Matematik max ${subjects.isEmpty ? "—" : subjects.map((s) => "${s.label} ${s.maxQuestions}").take(2).join(", ")}…). '
              'Bilmiyorsan atlayabilirsin; seviye testiyle netleşir.',
          mode: AnswerMode.subjectSliders,
          subjectLimits: subjects,
          choices: const [
            ChatChoice(id: 'skip_nets', label: 'Henüz bilmiyorum, atla'),
          ],
        );
      case WelcomeStep.strongSubjects:
        return ChatBubble(
          fromAi: true,
          text:
              'Hangi derslerde daha istikrarlısın?\n\n'
              'Bu seçim, planında koruma ve hız kazandırma bloklarını etkiler.',
          multiSelect: true,
          mode: AnswerMode.multiSelect,
          choices: _subjectChoicesFor(a.examType, a.branch),
        );
      case WelcomeStep.weakSubjects:
        return ChatBubble(
          fromAi: true,
          text:
              'Hangi derslerde öncelikli güçlendirme istiyorsun?\n\n'
              'Zayıf alanlar, ilk haftaların ana odak listesine girer.',
          multiSelect: true,
          mode: AnswerMode.multiSelect,
          choices: _subjectChoicesFor(a.examType, a.branch),
        );
      case WelcomeStep.studiedBefore:
        return ChatBubble(
          fromAi: true,
          text:
              '$examL’ye daha önce düzenli hazırlandın mı?\n\n'
              'Yeni başlayanlar için tempo daha yumuşak; '
              'deneyimliler için densite artar.',
          choices: const [
            ChatChoice(id: 'yes', label: 'Evet, düzenli çalıştım'),
            ChatChoice(id: 'no', label: 'Hayır, yeni başlıyorum'),
          ],
        );
      case WelcomeStep.habit:
        return const ChatBubble(
          fromAi: true,
          text:
              'Mevcut çalışma düzenin nasıl?\n\n'
              'Hatırlatma sıklığı ve plan esnekliği buna göre ayarlanır.',
          choices: [
            ChatChoice(id: 'duzenli', label: 'Düzenliyim — her gün bakarım'),
            ChatChoice(id: 'dalga', label: 'Dalgalı — bazen yoğun, bazen kopuk'),
            ChatChoice(id: 'yeni', label: 'Düzeni yeni kuruyorum'),
          ],
        );
      case WelcomeStep.studyStyle:
        return const ChatBubble(
          fromAi: true,
          text:
              'Çalışma tercihin hangisine daha yakın?\n\n'
              'Blok sırası (konu → soru → tekrar) buna göre kurulur.',
          choices: [
            ChatChoice(id: 'konu', label: 'Önce konu, sonra soru'),
            ChatChoice(id: 'soru', label: 'Bol soru / deneme ağırlıklı'),
            ChatChoice(id: 'tekrar', label: 'Tekrar ve pekiştirme ağırlıklı'),
            ChatChoice(id: 'karma', label: 'Dengeli / karışık program'),
          ],
        );
      case WelcomeStep.anythingElse:
        return const ChatBubble(
          fromAi: true,
          text:
              'Planı etkileyen ek bir kısıtın var mı?\n'
              '(İş/okul saatleri, engeller, özel hedef…)',
          freeTextHint: 'İstersen yaz…',
          mode: AnswerMode.freeText,
          choices: [
            ChatChoice(id: 'skip_extra', label: 'Yok, devam'),
          ],
        );
      case WelcomeStep.summary:
        final weak = a.weakSubjects.isEmpty
            ? 'seviye testinde netleşecek'
            : a.weakSubjects.join(', ');
        final hours = a.availableHours;
        final hoursLabel = hours == hours.roundToDouble()
            ? '${hours.toInt()} saat'
            : '${hours.toStringAsFixed(1)} saat';
        return ChatBubble(
          fromAi: true,
          text:
              'Teşekkürler $firstName.\n\n'
              '$examL · hedef ${a.targetNet.toStringAsFixed(0)} $scoreW · '
              'günlük $hoursLabel.\n'
              'Öncelikli güçlendirme: $weak.\n\n'
              'Sıradaki adım: ders ders seviye testi. '
              'Planın, test sonuçların ve çalışma verilerinle güncellenir.',
          choices: const [
            ChatChoice(id: 'go', label: 'Seviye testine geç'),
          ],
        );
      case WelcomeStep.done:
        return const ChatBubble(fromAi: true, text: '');
    }
  }

  List<ChatChoice> _subjectChoicesFor(String? exam, [String? branch]) {
    return subjectLimitsFor(exam, branch)
        .map((s) => ChatChoice(id: s.id, label: s.label))
        .toList();
  }

  WelcomeStep nextAfter(WelcomeStep step, WelcomeAnswers a) {
    switch (step) {
      case WelcomeStep.intro:
        return WelcomeStep.exam;
      case WelcomeStep.exam:
        if (needsYksBranch(a.examType) || needsKpssBranch(a.examType)) {
          return WelcomeStep.branch;
        }
        return WelcomeStep.education;
      case WelcomeStep.branch:
        return WelcomeStep.education;
      case WelcomeStep.education:
        return WelcomeStep.dailyTime;
      case WelcomeStep.dailyTime:
        return WelcomeStep.targetNet;
      case WelcomeStep.targetNet:
        return WelcomeStep.subjectNets;
      case WelcomeStep.subjectNets:
        return WelcomeStep.strongSubjects;
      case WelcomeStep.strongSubjects:
        return WelcomeStep.weakSubjects;
      case WelcomeStep.weakSubjects:
        return WelcomeStep.studiedBefore;
      case WelcomeStep.studiedBefore:
        return WelcomeStep.habit;
      case WelcomeStep.habit:
        return WelcomeStep.studyStyle;
      case WelcomeStep.studyStyle:
        return WelcomeStep.anythingElse;
      case WelcomeStep.anythingElse:
        return WelcomeStep.summary;
      case WelcomeStep.summary:
        return WelcomeStep.done;
      case WelcomeStep.done:
        return WelcomeStep.done;
    }
  }
}
