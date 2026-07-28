import '../../onboarding/domain/entities/learning_profile_entity.dart';

/// Sprint-3.1.C — resolve display name for legacy APIs from subject_code.
String? subjectNameForCode(LearningProfileEntity? profile, String? subjectCode) {
  if (profile == null || subjectCode == null || subjectCode.isEmpty) {
    return null;
  }
  for (final s in profile.subjects) {
    if (s.subjectCode == subjectCode) return s.subjectName;
  }
  return null;
}
