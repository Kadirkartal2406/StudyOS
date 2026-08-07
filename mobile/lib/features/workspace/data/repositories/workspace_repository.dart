import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/annotation_object.dart';
import '../datasources/workspace_local_datasource.dart';

final workspaceRepositoryProvider = Provider((ref) => WorkspaceRepository(WorkspaceLocalDatasource()));

class WorkspaceRepository {
  final WorkspaceLocalDatasource _localDatasource;

  WorkspaceRepository(this._localDatasource);

  Future<void> init() async {
    await _localDatasource.init();
  }

  Future<void> saveAnnotations(String workspaceId, String pageIndex, List<AnnotationObject> objects) async {
    await _localDatasource.saveAnnotations(workspaceId, pageIndex, objects);
  }

  Future<List<AnnotationObject>> getAnnotations(String workspaceId, String pageIndex) async {
    return await _localDatasource.getAnnotations(workspaceId, pageIndex);
  }

  Future<void> syncWithBackend(String workspaceId) async {
    // TODO: Connect to FastAPI backend endpoints via Dio to sync workspace and AnnotationLayers
  }
}
