import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/exam_catalog_remote_datasource.dart';

class ExamCatalogOption {
  const ExamCatalogOption({
    required this.code,
    required this.name,
    this.packCount = 0,
  });

  final String code;
  final String name;
  final int packCount;
}

class ExamPackOption {
  const ExamPackOption({
    required this.code,
    required this.name,
    this.branchKey,
  });

  final String code;
  final String name;
  final String? branchKey;
}

class ExamSubjectOption {
  const ExamSubjectOption({
    required this.code,
    required this.name,
    this.legacySubjectCode,
  });

  final String code;
  final String name;
  final String? legacySubjectCode;

  String get subjectCode =>
      (legacySubjectCode != null && legacySubjectCode!.isNotEmpty)
          ? legacySubjectCode!
          : code;
}

/// RC2 M22.1 — Exam Intelligence exams list.
final examCatalogExamsProvider =
    FutureProvider<List<ExamCatalogOption>>((ref) async {
  final api = ref.watch(examCatalogApiProvider);
  final rows = await api.listExams();
  return rows
      .map(
        (m) => ExamCatalogOption(
          code: (m['code'] ?? '').toString(),
          name: (m['name'] ?? m['code'] ?? '').toString(),
          packCount: (m['pack_count'] as num?)?.toInt() ?? 0,
        ),
      )
      .where((e) => e.code.isNotEmpty)
      .toList();
});

final examCatalogPacksProvider =
    FutureProvider.family<List<ExamPackOption>, String>((ref, exam) async {
  if (exam.isEmpty) return const [];
  final api = ref.watch(examCatalogApiProvider);
  final rows = await api.listPacks(exam);
  return rows
      .map(
        (m) => ExamPackOption(
          code: (m['code'] ?? '').toString(),
          name: (m['name'] ?? '').toString(),
          branchKey: m['branch_key']?.toString(),
        ),
      )
      .where((e) => e.code.isNotEmpty)
      .toList();
});

final examCatalogSubjectsProvider = FutureProvider.family<
    List<ExamSubjectOption>,
    ({String exam, String? branch})>((ref, args) async {
  if (args.exam.isEmpty) return const [];
  final api = ref.watch(examCatalogApiProvider);
  final rows = await api.listSubjects(
    args.exam,
    branch: args.branch,
  );
  return rows
      .map(
        (m) => ExamSubjectOption(
          code: (m['code'] ?? '').toString(),
          name: (m['name'] ?? '').toString(),
          legacySubjectCode: m['legacy_subject_code']?.toString(),
        ),
      )
      .where((e) => e.code.isNotEmpty)
      .toList();
});

final examCatalogTopicsProvider = FutureProvider.family<
    List<({String code, String name})>,
    ({String exam, String subject})>((ref, args) async {
  if (args.exam.isEmpty || args.subject.isEmpty) return const [];
  final api = ref.watch(examCatalogApiProvider);
  final rows = await api.listTopics(args.exam, args.subject);
  return rows
      .map((m) {
        final code = (m['code'] ?? '').toString();
        final name = (m['name'] ?? '').toString();
        return (code: code, name: name);
      })
      .where((t) => t.code.isNotEmpty)
      .toList();
});
