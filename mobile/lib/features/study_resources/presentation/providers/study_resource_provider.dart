import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/study_resource_remote_datasource.dart';
import '../../data/repositories/study_resource_repository_impl.dart';
import '../../domain/entities/study_resource_entity.dart';
import '../../domain/repositories/study_resource_repository.dart';
import 'study_resource_state.dart';

final _remoteProvider = Provider<StudyResourceRemoteDatasource>((ref) {
  return StudyResourceRemoteDatasource(ref.watch(dioClientProvider));
});

final studyResourceRepositoryProvider = Provider<StudyResourceRepository>((ref) {
  return StudyResourceRepositoryImpl(ref.watch(_remoteProvider));
});

/// Provider key: (studyPlanId, subjectCode, topicCode)
typedef ResourceKey = ({String? planId, String? subjectCode, String? topicCode});

class StudyResourceNotifier extends StateNotifier<StudyResourceState> {
  StudyResourceNotifier(this._repository, {this.studyPlanId, this.subjectCode, this.topicCode})
      : super(const StudyResourceInitial()) {
    load();
  }

  final StudyResourceRepository _repository;
  final String? studyPlanId;
  final String? subjectCode;
  final String? topicCode;

  Future<void> load() async {
    state = const StudyResourceLoading();
    try {
      final items = await _repository.listResources(
        studyPlanId: studyPlanId,
        subjectCode: subjectCode,
        topicCode: topicCode,
      );
      final stats = await _repository.getStatistics();
      state = StudyResourceLoaded(items: items, statistics: stats);
    } on AppException catch (e) {
      state = StudyResourceError(e.message);
    } catch (_) {
      state = const StudyResourceError('Kaynaklar yüklenemedi');
    }
  }

  Future<bool> create({
    required String title,
    required ResourceType resourceType,
    String? url,
    String? thumbnailUrl,
    String? provider,
    int? durationSeconds,
  }) async {
    try {
      await _repository.createResource(
        title: title,
        resourceType: resourceType,
        url: url,
        thumbnailUrl: thumbnailUrl,
        provider: provider,
        durationSeconds: durationSeconds,
        studyPlanId: studyPlanId,
        subjectCode: subjectCode,
        topicCode: topicCode,
      );
      await load();
      return true;
    } on AppException catch (e) {
      final current = state;
      if (current is StudyResourceLoaded) {
        state = current.copyWith(errorMessage: e.message);
      }
      return false;
    }
  }

  Future<void> setStatus(String id, ResourceStatus status) async {
    final current = state;
    if (current is! StudyResourceLoaded) return;
    try {
      await _repository.updateResource(id: id, status: status);
      await load();
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }

  Future<void> delete(String id) async {
    final current = state;
    if (current is! StudyResourceLoaded) return;
    try {
      await _repository.deleteResource(id);
      state = current.copyWith(
        items: current.items.where((e) => e.id != id).toList(),
        clearError: true,
      );
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }

  Future<StudyResourceEntity?> open(String id) async {
    try {
      return await _repository.openResource(id);
    } on AppException {
      return null;
    }
  }
}

final studyResourceProvider = StateNotifierProvider.family<
    StudyResourceNotifier, StudyResourceState, ResourceKey>((ref, key) {
  return StudyResourceNotifier(
    ref.watch(studyResourceRepositoryProvider),
    studyPlanId: key.planId,
    subjectCode: key.subjectCode,
    topicCode: key.topicCode,
  );
});
