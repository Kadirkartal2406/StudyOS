import '../../domain/entities/study_resource_entity.dart';
import '../../domain/repositories/study_resource_repository.dart';
import '../datasources/study_resource_remote_datasource.dart';

class StudyResourceRepositoryImpl implements StudyResourceRepository {
  const StudyResourceRepositoryImpl(this._remote);

  final StudyResourceRemoteDatasource _remote;

  @override
  Future<List<StudyResourceEntity>> listResources({
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
    ResourceStatus? status,
    ResourceType? resourceType,
  }) async {
    final models = studyPlanId != null
        ? await _remote.listPlanResources(studyPlanId)
        : await _remote.listResources(
            studyPlanId: studyPlanId,
            subjectCode: subjectCode,
            topicCode: topicCode,
            status: status?.apiValue,
            resourceType: resourceType?.apiValue,
          );
    return models.map((e) => e.toEntity()).toList();
  }

  @override
  Future<StudyResourceEntity> getResource(String id) async {
    return (await _remote.getResource(id)).toEntity();
  }

  @override
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
  }) async {
    final body = <String, dynamic>{
      'title': title,
      'resource_type': resourceType.apiValue,
      'status': status.apiValue,
      if (description != null) 'description': description,
      if (url != null) 'url': url,
      if (thumbnailUrl != null) 'thumbnail_url': thumbnailUrl,
      if (provider != null) 'provider': provider,
      if (durationSeconds != null) 'duration_seconds': durationSeconds,
      if (author != null) 'author': author,
      if (studyPlanId != null) 'study_plan_id': studyPlanId,
      if (subjectCode != null) 'subject_code': subjectCode,
      if (topicCode != null) 'topic_code': topicCode,
    };
    final model = studyPlanId != null
        ? await _remote.createPlanResource(studyPlanId, body)
        : await _remote.createResource(body);
    return model.toEntity();
  }

  @override
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
  }) async {
    final body = <String, dynamic>{
      if (title != null) 'title': title,
      if (resourceType != null) 'resource_type': resourceType.apiValue,
      if (description != null) 'description': description,
      if (url != null) 'url': url,
      if (thumbnailUrl != null) 'thumbnail_url': thumbnailUrl,
      if (provider != null) 'provider': provider,
      if (durationSeconds != null) 'duration_seconds': durationSeconds,
      if (author != null) 'author': author,
      if (studyPlanId != null) 'study_plan_id': studyPlanId,
      if (status != null) 'status': status.apiValue,
      if (orderIndex != null) 'order_index': orderIndex,
    };
    return (await _remote.updateResource(id, body)).toEntity();
  }

  @override
  Future<void> deleteResource(String id) => _remote.deleteResource(id);

  @override
  Future<StudyResourceEntity> openResource(String id) async {
    return (await _remote.openResource(id)).toEntity();
  }

  @override
  Future<ResourceStatisticsEntity> getStatistics() async {
    return (await _remote.getStatistics()).toEntity();
  }

  @override
  Future<String> uploadResourceFile(
    List<int> fileBytes,
    String filename, {
    String? filePath,
  }) {
    return _remote.uploadResourceFile(
      fileBytes,
      filename,
      filePath: filePath,
    );
  }
}
