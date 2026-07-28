import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';
import '../../domain/entities/topic_notebook_entity.dart';

typedef TopicKey = ({String subjectCode, String topicCode});

final topicNotebookProvider = FutureProvider.family<TopicNotebookEntity, TopicKey>(
  (ref, key) async {
    final dio = ref.watch(dioClientProvider);
    final response = await dio.get<Map<String, dynamic>>(
      ApiEndpoints.topicNotebook(key.subjectCode, key.topicCode),
    );
    final data = response.data;
    if (data == null || data['data'] == null) {
      throw Exception('Invalid Notebook response');
    }
    return TopicNotebookEntity.fromJson(data['data'] as Map<String, dynamic>);
  },
);
