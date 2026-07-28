import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../../../core/network/dio_client.dart';
import '../../../exam_catalog/presentation/providers/exam_catalog_provider.dart';
import '../../../onboarding/presentation/providers/active_exam_provider.dart';

class TopicOption {
  const TopicOption({required this.code, required this.name});
  final String code;
  final String name;
}

/// RC2 M22.1 — Topics from Exam Intelligence when active exam known;
/// legacy learning-profile catalog fallback.
final subjectTopicsProvider =
    FutureProvider.family<List<TopicOption>, String>((ref, subjectCode) async {
  if (subjectCode.isEmpty) return [];

  final activeExam =
      ref.watch(activeExamControllerProvider).activeExamType?.toLowerCase();

  if (activeExam != null && activeExam.isNotEmpty) {
    try {
      final topics = await ref.watch(
        examCatalogTopicsProvider((exam: activeExam, subject: subjectCode))
            .future,
      );
      if (topics.isNotEmpty) {
        return [
          for (final t in topics) TopicOption(code: t.code, name: t.name),
        ];
      }
    } catch (_) {
      // fall through to legacy
    }
  }

  final dio = ref.watch(dioClientProvider);
  try {
    final response = await dio.get<Map<String, dynamic>>(
      ApiEndpoints.subjectTopics(subjectCode),
    );
    final body = response.data;
    final data = body?['data'];
    final List<dynamic> items;
    if (data is List) {
      items = data;
    } else if (data is Map && data['topics'] is List) {
      items = data['topics'] as List;
    } else {
      items = [];
    }
    return items
        .map((e) {
          final m = e as Map<String, dynamic>;
          return TopicOption(
            code: (m['topic_code'] ?? m['code'] ?? '').toString(),
            name: (m['topic_name'] ?? m['name'] ?? '').toString(),
          );
        })
        .where((t) => t.code.isNotEmpty)
        .toList();
  } on DioException catch (e) {
    throw dioExceptionToAppException(e);
  }
});
