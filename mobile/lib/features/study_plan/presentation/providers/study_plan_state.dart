import '../../domain/entities/study_plan_entity.dart';

/// StudyPlan feature için mühürlü (sealed) durum sınıfı.
/// Dart 3 sealed class — exhaustive switch garantisi.
sealed class StudyPlanState {
  const StudyPlanState();
}

/// İlk yüklenme — henüz istek atılmadı.
class StudyPlanInitial extends StudyPlanState {
  const StudyPlanInitial();
}

/// Seçilen güne ait planlar yükleniyor.
class StudyPlanLoading extends StudyPlanState {
  const StudyPlanLoading(this.selectedDate);

  final DateTime selectedDate;
}

/// Planlar başarıyla yüklendi.
class StudyPlanLoaded extends StudyPlanState {
  const StudyPlanLoaded({
    required this.selectedDate,
    required this.plans,
    this.mutatingPlanId,
  });

  final DateTime selectedDate;
  final List<StudyPlanEntity> plans;

  /// Start/complete/skip/delete gibi tekil bir plan üzerindeki işlem sürerken
  /// ilgili kartta yerel bir yükleniyor göstergesi için kullanılır.
  final String? mutatingPlanId;

  int get completedCount =>
      plans.where((p) => p.status.name == 'completed').length;

  int get totalMinutes => plans.fold(0, (sum, p) => sum + p.completedMinutes);

  int get totalQuestions =>
      plans.fold(0, (sum, p) => sum + p.completedQuestionCount);

  int get estimatedTotalMinutes =>
      plans.fold(0, (sum, p) => sum + p.estimatedMinutes);

  double get progressPercentage {
    if (estimatedTotalMinutes <= 0) return 0.0;
    return (totalMinutes / estimatedTotalMinutes * 100).clamp(0.0, 100.0);
  }

  StudyPlanLoaded copyWith({
    List<StudyPlanEntity>? plans,
    String? mutatingPlanId,
    bool clearMutatingPlanId = false,
  }) {
    return StudyPlanLoaded(
      selectedDate: selectedDate,
      plans: plans ?? this.plans,
      mutatingPlanId:
          clearMutatingPlanId ? null : (mutatingPlanId ?? this.mutatingPlanId),
    );
  }
}

/// Planlar yüklenirken hata oluştu.
class StudyPlanError extends StudyPlanState {
  const StudyPlanError(this.selectedDate, this.message);

  final DateTime selectedDate;
  final String message;
}
