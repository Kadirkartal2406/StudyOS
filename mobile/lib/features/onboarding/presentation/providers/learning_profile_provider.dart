import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../question_tracking/domain/entities/question_enums.dart';
import '../../domain/entities/learning_profile_entity.dart';
import 'onboarding_provider.dart';

/// Learning Profile — uygulamanın tek doğruluk kaynağı (Sprint-3.0.1 SSOT).
final learningProfileProvider =
    FutureProvider<LearningProfileEntity>((ref) async {
  final auth = ref.watch(authProvider);
  if (auth is! AuthAuthenticated) {
    throw StateError('Learning profile requires authentication');
  }
  return ref.watch(learningProfileRepositoryProvider).getProfile();
});

/// Profil değişince tüm tüketicileri yenile.
void invalidateLearningProfile(WidgetRef ref) {
  ref.invalidate(learningProfileProvider);
}

extension LearningProfileDefaults on LearningProfileEntity {
  /// Backend primary_exam_type; yoksa exam_targets'tan türet.
  String? get resolvedPrimaryExamType {
    if (primaryExamType != null && primaryExamType!.isNotEmpty) {
      return primaryExamType;
    }
    for (final t in examTargets) {
      if (t.isPrimary) return t.examType;
    }
    return examTargets.isEmpty ? null : examTargets.first.examType;
  }

  ExamType? get primaryExamTypeEnum => ExamType.fromApi(resolvedPrimaryExamType);

  /// Kullanıcının exam_targets + YKS ise TYT/AYT alt türleri.
  List<String> get allowedExamTypes {
    final types = examTargets.map((e) => e.examType).toSet();
    if (types.contains('yks')) {
      types.addAll({'tyt', 'ayt'});
    }
    if (types.isEmpty) {
      return const [
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
    }
    final list = types.toList()..sort();
    return list;
  }

  /// Active switcher için — sadece exam_targets (TYT/AYT ekleme yok).
  List<String> get switchableExamTypes {
    final types = examTargets.map((e) => e.examType).toSet().toList()..sort();
    return types;
  }

  List<ExamType> get allowedExamTypeEnums => allowedExamTypes
      .map(ExamType.fromApi)
      .whereType<ExamType>()
      .toList();

  List<UserSubjectEntity> get activeSubjects {
    final active = subjects.where((s) => s.isActive).toList();
    final exam = (activeExamType ?? primaryExamType)?.toLowerCase();
    if (exam == null || exam.isEmpty) return active;

    // YKS → TYT/AYT subject_code prefix'leri; diğerleri `${exam}_`
    final prefixes = exam == 'yks'
        ? const {'tyt_', 'ayt_', 'yks_'}
        : {'${exam}_'};
    final scoped = active
        .where(
          (s) => prefixes.any(
            (p) => s.subjectCode.toLowerCase().startsWith(p),
          ),
        )
        .toList();
    // Prefix eşleşmezse backend zaten filtrelediyse tüm aktifleri göster
    return scoped.isNotEmpty ? scoped : active;
  }

  List<String> get subjectNames =>
      activeSubjects.map((s) => s.subjectName).toList();
}
