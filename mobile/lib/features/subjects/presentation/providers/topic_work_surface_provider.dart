import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/network/dio_client.dart';
import '../../data/datasources/topic_work_surface_remote_datasource.dart';
import '../../domain/entities/topic_work_surface_entity.dart';

typedef TopicWorkSurfaceKey = ({String subjectCode, String topicCode});

final _topicWorkSurfaceRemoteProvider = Provider((ref) {
  return TopicWorkSurfaceRemoteDatasource(ref.watch(dioClientProvider));
});

/// Alignment Sprint-3 — Work Surface projection (Decision uygular).
final topicWorkSurfaceProvider = FutureProvider.family<TopicWorkSurfaceEntity,
    TopicWorkSurfaceKey>((ref, key) async {
  return ref.watch(_topicWorkSurfaceRemoteProvider).getWorkSurface(
        subjectCode: key.subjectCode,
        topicCode: key.topicCode,
      );
});
