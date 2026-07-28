/// Dashboard / timeline aktivite kaydı (Sprint-1.7).
class ActivityEntity {
  const ActivityEntity({
    required this.id,
    required this.eventType,
    required this.title,
    required this.occurredAt,
    this.description,
    this.studySessionId,
    this.studyPlanId,
  });

  final String id;
  final String eventType;
  final String title;
  final String? description;
  final String? studySessionId;
  final String? studyPlanId;
  final DateTime occurredAt;
}
