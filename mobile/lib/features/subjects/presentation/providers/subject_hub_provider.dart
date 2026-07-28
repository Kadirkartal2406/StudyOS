import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/network/dio_client.dart';
import '../../data/datasources/subject_hub_remote_datasource.dart';
import '../../domain/entities/subject_hub_entity.dart';

final _subjectHubRemoteProvider = Provider((ref) {
  return SubjectHubRemoteDatasource(ref.watch(dioClientProvider));
});

/// Sprint-3.1.C — hub by subject_code only.
final subjectHubProvider =
    FutureProvider.family<SubjectHubEntity, String>((ref, subjectCode) async {
  return ref.watch(_subjectHubRemoteProvider).getHub(subjectCode);
});
