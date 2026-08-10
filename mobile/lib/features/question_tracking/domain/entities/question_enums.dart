/// Sınav türü enum — backend ExamType / exam_identity ile senkron.
enum ExamType {
  kpssLisans,
  kpssOnlisans,
  kpssOrtaogretim,
  tyt,
  aytSayisal,
  aytEa,
  aytSozel,
  ydtIngilizce,
  yks,
  ags,
  lgs,
  ales,
  dgs,
  ydsIngilizce,
  yokdilIngilizce,
  custom,

  // Legacy aliases kept for older local caches / question records
  ayt,
  kpss,
  yds;

  String get apiValue => switch (this) {
        ExamType.kpssLisans => 'kpss_lisans',
        ExamType.kpssOnlisans => 'kpss_onlisans',
        ExamType.kpssOrtaogretim => 'kpss_ortaogretim',
        ExamType.tyt => 'tyt',
        ExamType.aytSayisal => 'ayt_sayisal',
        ExamType.aytEa => 'ayt_ea',
        ExamType.aytSozel => 'ayt_sozel',
        ExamType.ydtIngilizce => 'ydt_ingilizce',
        ExamType.yks => 'yks',
        ExamType.ags => 'ags',
        ExamType.lgs => 'lgs',
        ExamType.ales => 'ales',
        ExamType.dgs => 'dgs',
        ExamType.ydsIngilizce => 'yds_ingilizce',
        ExamType.yokdilIngilizce => 'yokdil_ingilizce',
        ExamType.custom => 'custom',
        ExamType.ayt => 'ayt',
        ExamType.kpss => 'kpss',
        ExamType.yds => 'yds',
      };

  static ExamType? fromApi(String? value) {
    if (value == null) return null;
    final v = value.trim().toLowerCase();
    for (final e in ExamType.values) {
      if (e.apiValue == v) return e;
    }
    return switch (v) {
      'yokdil' => ExamType.yokdilIngilizce,
      'ydt' => ExamType.ydtIngilizce,
      _ => null,
    };
  }

  String get label => switch (this) {
        ExamType.kpssLisans => 'KPSS Lisans',
        ExamType.kpssOnlisans => 'KPSS Önlisans',
        ExamType.kpssOrtaogretim => 'KPSS Ortaöğretim',
        ExamType.tyt => 'TYT',
        ExamType.aytSayisal => 'AYT Sayısal',
        ExamType.aytEa => 'AYT Eşit Ağırlık',
        ExamType.aytSozel => 'AYT Sözel',
        ExamType.ydtIngilizce => 'YDT İngilizce',
        ExamType.yks => 'YKS',
        ExamType.ags => 'AGS',
        ExamType.lgs => 'LGS',
        ExamType.ales => 'ALES',
        ExamType.dgs => 'DGS',
        ExamType.ydsIngilizce => 'YDS İngilizce',
        ExamType.yokdilIngilizce => 'YÖKDİL İngilizce',
        ExamType.custom => 'Özel',
        ExamType.ayt => 'AYT',
        ExamType.kpss => 'KPSS',
        ExamType.yds => 'YDS',
      };
}

enum QuestionDifficulty {
  easy,
  medium,
  hard;

  String get apiValue => name;

  static QuestionDifficulty? fromApi(String? value) {
    if (value == null) return null;
    for (final e in QuestionDifficulty.values) {
      if (e.name == value) return e;
    }
    return null;
  }

  String get label => switch (this) {
        QuestionDifficulty.easy => 'Kolay',
        QuestionDifficulty.medium => 'Orta',
        QuestionDifficulty.hard => 'Zor',
      };
}

enum QuestionSource {
  book,
  video,
  pastExam,
  online,
  classSource,
  other;

  String get apiValue => switch (this) {
        QuestionSource.book => 'book',
        QuestionSource.video => 'video',
        QuestionSource.pastExam => 'past_exam',
        QuestionSource.online => 'online',
        QuestionSource.classSource => 'class',
        QuestionSource.other => 'other',
      };

  static QuestionSource? fromApi(String? value) {
    if (value == null) return null;
    return switch (value) {
      'book' => QuestionSource.book,
      'video' => QuestionSource.video,
      'past_exam' => QuestionSource.pastExam,
      'online' => QuestionSource.online,
      'class' => QuestionSource.classSource,
      'other' => QuestionSource.other,
      _ => null,
    };
  }

  String get label => switch (this) {
        QuestionSource.book => 'Kitap',
        QuestionSource.video => 'Video',
        QuestionSource.pastExam => 'Çıkmış Soru',
        QuestionSource.online => 'Online',
        QuestionSource.classSource => 'Ders',
        QuestionSource.other => 'Diğer',
      };
}
