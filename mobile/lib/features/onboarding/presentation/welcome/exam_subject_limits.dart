/// Onboarding — sınav dersleri ve resmi soru sayıları (net üst sınırı).
/// Backend `exam_question_blueprint.py` ile uyumlu tutulur.
library;

class SubjectNetLimit {
  const SubjectNetLimit({required this.id, required this.label, required this.maxQuestions});

  final String id;
  final String label;
  /// O dersteki resmi soru sayısı → net slider max.
  final int maxQuestions;
}

class ExamScoreLimits {
  const ExamScoreLimits({
    required this.targetMax,
    required this.scoreWord,
    this.targetMin = 0,
    this.targetDivisions,
  });

  final double targetMin;
  final double targetMax;
  final String scoreWord; // net | puan
  final int? targetDivisions;
}

/// Hedef skor üst sınırı (sınav formu).
ExamScoreLimits scoreLimitsFor(String? exam, [String? branch]) {
  final e = (exam ?? '').toLowerCase();
  if (e == 'lgs') {
    return const ExamScoreLimits(
      targetMin: 200,
      targetMax: 500,
      scoreWord: 'puan',
      targetDivisions: 60,
    );
  }
  if (e == 'ags') {
    return const ExamScoreLimits(
      targetMin: 10,
      targetMax: 80,
      scoreWord: 'net',
      targetDivisions: 70,
    );
  }
  if (e == 'ales' || e == 'yds' || e == 'yds_ingilizce' || e == 'yokdil' || e == 'yokdil_ingilizce' || e == 'ydt' || e == 'ydt_ingilizce') {
    return const ExamScoreLimits(
      targetMin: 40,
      targetMax: 100,
      scoreWord: 'puan',
      targetDivisions: 60,
    );
  }
  if (e == 'ayt') {
    final b = (branch ?? 'sayisal').toLowerCase();
    final max = switch (b) {
      'dil' => 80.0,
      'sozel' => 80.0,
      'ea' => 80.0,
      _ => 80.0,
    };
    return ExamScoreLimits(
      targetMin: 10,
      targetMax: max,
      scoreWord: 'net',
      targetDivisions: max.toInt(),
    );
  }
  if (e == 'tyt') {
    return const ExamScoreLimits(
      targetMin: 20,
      targetMax: 120,
      scoreWord: 'net',
      targetDivisions: 100,
    );
  }
  if (e == 'yks') {
    return const ExamScoreLimits(
      targetMin: 40,
      targetMax: 200,
      scoreWord: 'net',
      targetDivisions: 160,
    );
  }
  if (e == 'dgs') {
    return const ExamScoreLimits(
      targetMin: 20,
      targetMax: 120,
      scoreWord: 'net',
      targetDivisions: 100,
    );
  }
  // kpss / ags / default
  return const ExamScoreLimits(
    targetMin: 20,
    targetMax: 120,
    scoreWord: 'net',
    targetDivisions: 100,
  );
}

List<SubjectNetLimit> subjectLimitsFor(String? exam, [String? branch]) {
  final e = (exam ?? 'kpss').toLowerCase();
  final b = (branch ?? '').toLowerCase();

  if (e == 'yds' || e == 'yds_ingilizce' || e == 'yokdil' || e == 'yokdil_ingilizce') {
    return const [
      SubjectNetLimit(id: 'İngilizce', label: 'İngilizce', maxQuestions: 80),
    ];
  }
  if (e == 'ydt' || e == 'ydt_ingilizce') {
    return const [
      SubjectNetLimit(id: 'İngilizce', label: 'İngilizce', maxQuestions: 80),
    ];
  }
  if (e == 'ags') {
    return const [
      SubjectNetLimit(id: 'Türkçe', label: 'Türkçe', maxQuestions: 40),
      SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 40),
    ];
  }
  if (e == 'ales') {
    return const [
      SubjectNetLimit(id: 'Sayısal', label: 'Sayısal', maxQuestions: 50),
      SubjectNetLimit(id: 'Sözel', label: 'Sözel', maxQuestions: 50),
    ];
  }
  if (e == 'dgs') {
    return const [
      SubjectNetLimit(id: 'Sayısal', label: 'Sayısal', maxQuestions: 60),
      SubjectNetLimit(id: 'Sözel', label: 'Sözel', maxQuestions: 60),
    ];
  }
  if (e == 'lgs') {
    if (b == 'sayisal') {
      return const [
        SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 20),
        SubjectNetLimit(id: 'Fen', label: 'Fen Bilimleri', maxQuestions: 20),
      ];
    }
    if (b == 'sozel') {
      return const [
        SubjectNetLimit(id: 'Türkçe', label: 'Türkçe', maxQuestions: 20),
        SubjectNetLimit(id: 'İnkılap', label: 'T.C. İnkılap Tarihi', maxQuestions: 10),
        SubjectNetLimit(id: 'Din', label: 'Din Kültürü', maxQuestions: 10),
        SubjectNetLimit(id: 'İngilizce', label: 'İngilizce', maxQuestions: 10),
      ];
    }
    return const [
      SubjectNetLimit(id: 'Türkçe', label: 'Türkçe', maxQuestions: 20),
      SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 20),
      SubjectNetLimit(id: 'Fen', label: 'Fen Bilimleri', maxQuestions: 20),
      SubjectNetLimit(id: 'İnkılap', label: 'T.C. İnkılap Tarihi', maxQuestions: 10),
      SubjectNetLimit(id: 'Din', label: 'Din Kültürü', maxQuestions: 10),
      SubjectNetLimit(id: 'İngilizce', label: 'İngilizce', maxQuestions: 10),
    ];
  }
  if (e == 'tyt') {
    return const [
      SubjectNetLimit(id: 'Türkçe', label: 'Türkçe', maxQuestions: 40),
      SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 30),
      SubjectNetLimit(id: 'Geometri', label: 'Geometri', maxQuestions: 10),
      SubjectNetLimit(id: 'Fizik', label: 'Fizik', maxQuestions: 7),
      SubjectNetLimit(id: 'Kimya', label: 'Kimya', maxQuestions: 7),
      SubjectNetLimit(id: 'Biyoloji', label: 'Biyoloji', maxQuestions: 6),
      SubjectNetLimit(id: 'Tarih', label: 'Tarih', maxQuestions: 5),
      SubjectNetLimit(id: 'Coğrafya', label: 'Coğrafya', maxQuestions: 5),
      SubjectNetLimit(id: 'Felsefe', label: 'Felsefe', maxQuestions: 5),
      SubjectNetLimit(id: 'Din', label: 'Din', maxQuestions: 5),
    ];
  }
  if (e == 'ayt' || e == 'ayt_sayisal' || e == 'ayt_ea' || e == 'ayt_sozel' || e == 'yks') {
    final aytBranch = e.startsWith('ayt_') ? e.substring(4) : b;
    final ayt = switch (aytBranch) {
      'ea' => const [
          SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 30),
          SubjectNetLimit(id: 'Geometri', label: 'Geometri', maxQuestions: 10),
          SubjectNetLimit(id: 'Edebiyat', label: 'Edebiyat', maxQuestions: 24),
          SubjectNetLimit(id: 'Tarih', label: 'Tarih', maxQuestions: 10),
          SubjectNetLimit(id: 'Coğrafya', label: 'Coğrafya', maxQuestions: 6),
        ],
      'sozel' => const [
          SubjectNetLimit(id: 'Edebiyat', label: 'Edebiyat', maxQuestions: 24),
          SubjectNetLimit(id: 'Tarih', label: 'Tarih', maxQuestions: 21),
          SubjectNetLimit(id: 'Coğrafya', label: 'Coğrafya', maxQuestions: 17),
          SubjectNetLimit(id: 'Felsefe', label: 'Felsefe', maxQuestions: 12),
          SubjectNetLimit(id: 'Din', label: 'Din', maxQuestions: 6),
        ],
      'dil' || 'en' => const [
          SubjectNetLimit(id: 'İngilizce', label: 'YDT İngilizce', maxQuestions: 80),
        ],
      _ => const [
          SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 30),
          SubjectNetLimit(id: 'Geometri', label: 'Geometri', maxQuestions: 10),
          SubjectNetLimit(id: 'Fizik', label: 'Fizik', maxQuestions: 14),
          SubjectNetLimit(id: 'Kimya', label: 'Kimya', maxQuestions: 13),
          SubjectNetLimit(id: 'Biyoloji', label: 'Biyoloji', maxQuestions: 13),
        ],
    };
    if (e == 'yks') {
      // TYT çekirdek + AYT/YDT alanı
      return [
        const SubjectNetLimit(id: 'Türkçe', label: 'TYT Türkçe', maxQuestions: 40),
        const SubjectNetLimit(id: 'TYT Matematik', label: 'TYT Matematik', maxQuestions: 30),
        const SubjectNetLimit(id: 'Geometri', label: 'TYT Geometri', maxQuestions: 10),
        ...ayt,
      ];
    }
    return ayt;
  }
  // KPSS variants
  return const [
    SubjectNetLimit(id: 'Türkçe', label: 'Türkçe', maxQuestions: 30),
    SubjectNetLimit(id: 'Matematik', label: 'Matematik', maxQuestions: 30),
    SubjectNetLimit(id: 'Tarih', label: 'Tarih', maxQuestions: 27),
    SubjectNetLimit(id: 'Coğrafya', label: 'Coğrafya', maxQuestions: 18),
    SubjectNetLimit(id: 'Vatandaşlık', label: 'Vatandaşlık', maxQuestions: 9),
    SubjectNetLimit(id: 'Güncel', label: 'Güncel Bilgiler', maxQuestions: 6),
  ];
}

/// Sınava göre anlamlı eğitim / durum seçenekleri.
List<({String id, String label})> educationChoicesFor(String? exam) {
  final e = (exam ?? '').toLowerCase();
  if (e == 'lgs') {
    return const [
      (id: 'ortaokul_7', label: '7. sınıftayım'),
      (id: 'ortaokul_8', label: '8. sınıftayım'),
      (id: 'mezun_ortaokul', label: 'Ortaokul mezunuyum (tekrar)'),
      (id: 'ozel', label: 'Özel hazırlık / açık öğretim'),
    ];
  }
  if (e == 'yks' || e == 'tyt' || e == 'ayt') {
    return const [
      (id: 'lise_9_10', label: '9–10. sınıftayım'),
      (id: 'lise_11', label: '11. sınıftayım'),
      (id: 'lise_12', label: '12. sınıftayım'),
      (id: 'mezun_lise', label: 'Lise mezunuyum'),
      (id: 'acik', label: 'Açık öğretim / yeniden hazırlanıyorum'),
    ];
  }
  if (e == 'ales') {
    return const [
      (id: 'lisans_son', label: 'Lisans son sınıf / bitirmek üzereyim'),
      (id: 'lisans_mezun', label: 'Lisans mezunuyum'),
      (id: 'yl_hazirlik', label: 'Yüksek lisans / doktora hazırlığı'),
      (id: 'calisiyor', label: 'Çalışıyorum (meslek / akademik)'),
    ];
  }
  if (e == 'dgs') {
    return const [
      (id: 'onlisans_ogrenci', label: 'Önlisans öğrencisiyim'),
      (id: 'onlisans_mezun', label: 'Önlisans mezunuyum'),
      (id: 'calisiyor', label: 'Çalışıyorum'),
      (id: 'tekrar', label: 'Yeniden hazırlanıyorum'),
    ];
  }
  if (e == 'yds' || e == 'yokdil') {
    return const [
      (id: 'uni_ogrenci', label: 'Üniversite öğrencisiyim'),
      (id: 'mezun', label: 'Mezunum'),
      (id: 'akademik', label: 'Akademik kariyer / atama'),
      (id: 'calisiyor', label: 'Çalışıyorum / kamu personeliyim'),
    ];
  }
  if (e == 'kpss' || e == 'ags') {
    return const [
      (id: 'uni_ogrenci', label: 'Üniversite öğrencisiyim'),
      (id: 'mezun', label: 'Üniversite mezunuyum'),
      (id: 'onlisans', label: 'Önlisans mezunuyum'),
      (id: 'calisiyor', label: 'Çalışıyorum'),
      (id: 'tekrar', label: 'Yeniden hazırlanıyorum'),
    ];
  }
  return const [
    (id: 'ogrenci', label: 'Öğrenciyim'),
    (id: 'mezun', label: 'Mezunum'),
    (id: 'calisiyor', label: 'Çalışıyorum'),
    (id: 'tekrar', label: 'Yeniden hazırlanıyorum'),
  ];
}
