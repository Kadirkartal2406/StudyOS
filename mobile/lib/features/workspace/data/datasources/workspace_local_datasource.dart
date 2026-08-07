import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';
import '../../domain/entities/annotation_object.dart';

class WorkspaceLocalDatasource {
  static const String boxName = 'workspace_annotations_box';

  Future<void> init() async {
    await Hive.initFlutter();
    await Hive.openBox(boxName);
  }

  Future<void> saveAnnotations(String workspaceId, String pageIndex, List<AnnotationObject> objects) async {
    final box = Hive.box(boxName);
    final key = '${workspaceId}_$pageIndex';
    final objectsJson = objects.map((o) => o.toJson()).toList();
    await box.put(key, jsonEncode(objectsJson));
  }

  Future<List<AnnotationObject>> getAnnotations(String workspaceId, String pageIndex) async {
    final box = Hive.box(boxName);
    final key = '${workspaceId}_$pageIndex';
    
    final data = box.get(key);
    if (data == null) return [];

    try {
      final List<dynamic> parsed = jsonDecode(data);
      return parsed.map((json) => AnnotationObject.fromJson(json as Map<String, dynamic>)).toList();
    } catch (e) {
      return [];
    }
  }

  Future<void> clearWorkspace(String workspaceId) async {
    final box = Hive.box(boxName);
    final keysToDelete = box.keys.where((k) => k.toString().startsWith('${workspaceId}_')).toList();
    await box.deleteAll(keysToDelete);
  }
}
