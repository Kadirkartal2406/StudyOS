/// Sınav türü enum — backend ExamType ile senkron.
enum ExamType {
  tyt,
  ayt,
  yks,
  lgs,
  kpss,
  ales,
  dgs,
  yds,
  custom;

  String get apiValue => name;

  static ExamType? fromApi(String? value) {
    if (value == null) return null;
    for (final e in ExamType.values) {
      if (e.name == value) return e;
    }
    return null;
  }

  String get label => switch (this) {
        ExamType.tyt => 'TYT',
        ExamType.ayt => 'AYT',
        ExamType.yks => 'YKS',
        ExamType.lgs => 'LGS',
        ExamType.kpss => 'KPSS',
        ExamType.ales => 'ALES',
        ExamType.dgs => 'DGS',
        ExamType.yds => 'YDS',
        ExamType.custom => 'Özel',
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
