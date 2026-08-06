import '../entities/study_resource_entity.dart';

abstract class StudyResourceRepository {
  Future<List<StudyResourceEntity>> listResources({
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
    ResourceStatus? status,
    ResourceType? resourceType,
  });

  Future<StudyResourceEntity> getResource(String id);

  Future<StudyResourceEntity> createResource({
    required String title,
    required ResourceType resourceType,
    String? description,
    String? url,
    String? thumbnailUrl,
    String? provider,
    int? durationSeconds,
    String? author,
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
    ResourceStatus status = ResourceStatus.notStarted,
  });

  Future<StudyResourceEntity> updateResource({
    required String id,
    String? title,
    ResourceType? resourceType,
    String? description,
    String? url,
    String? thumbnailUrl,
    String? provider,
    int? durationSeconds,
    String? author,
    String? studyPlanId,
    ResourceStatus? status,
    int? orderIndex,
  });

  Future<void> deleteResource(String id);

  Future<StudyResourceEntity> openResource(String id);

  Future<ResourceStatisticsEntity> getStatistics();

  Future<String> uploadResourceFile(
    List<int> fileBytes,
    String filename, {
    String? filePath,
  });
}
