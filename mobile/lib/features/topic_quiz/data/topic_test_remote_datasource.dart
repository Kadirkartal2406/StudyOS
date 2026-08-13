import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/app_exception.dart';
import '../../../core/errors/dio_exception_mapper.dart';
import '../../../core/network/dio_client.dart';

class TopicTestListItem {
  const TopicTestListItem({
    required this.id,
    required this.weekId,
    required this.difficulty,
    required this.ordinal,
    required this.questionCount,
    required this.title,
    this.userStatus,
    this.accuracyPct,
    this.attemptId,
    this.publishedAt,
  });

  final String id;
  final String weekId;
  final String difficulty;
  final int ordinal;
  final int questionCount;
  final String title;
  final String? userStatus;
  final double? accuracyPct;
  final String? attemptId;
  final String? publishedAt;

  factory TopicTestListItem.fromJson(Map<String, dynamic> json) {
    return TopicTestListItem(
      id: '${json['id']}',
      weekId: json['week_id'] as String? ?? '',
      difficulty: json['difficulty'] as String? ?? 'medium',
      ordinal: json['ordinal'] as int? ?? 1,
      questionCount: json['question_count'] as int? ?? 10,
      title: json['title'] as String? ?? 'Test',
      userStatus: json['user_status'] as String?,
      accuracyPct: (json['accuracy_pct'] as num?)?.toDouble(),
      attemptId: json['attempt_id']?.toString(),
      publishedAt: json['published_at']?.toString(),
    );
  }
}

class TopicTestCatalog {
  const TopicTestCatalog({
    required this.exam,
    required this.subjectCode,
    required this.topicCode,
    required this.tests,
    this.subjectName,
    this.topicName,
  });

  final String exam;
  final String subjectCode;
  final String topicCode;
  final String? subjectName;
  final String? topicName;
  final List<TopicTestListItem> tests;

  factory TopicTestCatalog.fromJson(Map<String, dynamic> json) {
    final tests = (json['tests'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(TopicTestListItem.fromJson)
        .toList();
    return TopicTestCatalog(
      exam: json['exam'] as String? ?? '',
      subjectCode: json['subject_code'] as String? ?? '',
      topicCode: json['topic_code'] as String? ?? '',
      subjectName: json['subject_name'] as String?,
      topicName: json['topic_name'] as String?,
      tests: tests,
    );
  }
}

class TopicTestChoiceItem {
  const TopicTestChoiceItem({
    required this.id,
    required this.ordIndex,
    required this.stem,
    required this.choices,
  });

  final String id;
  final int ordIndex;
  final String stem;
  final Map<String, String> choices;

  factory TopicTestChoiceItem.fromJson(Map<String, dynamic> json) {
    final raw = json['choices'];
    final choices = <String, String>{};
    if (raw is Map) {
      for (final e in raw.entries) {
        choices['${e.key}'] = '${e.value}';
      }
    }
    return TopicTestChoiceItem(
      id: '${json['id']}',
      ordIndex: json['ord_index'] as int? ?? 0,
      stem: json['stem'] as String? ?? '',
      choices: choices,
    );
  }
}

class TopicTestAttempt {
  const TopicTestAttempt({
    required this.attemptId,
    required this.testId,
    required this.weekId,
    required this.difficulty,
    required this.ordinal,
    required this.status,
    required this.questionCount,
    required this.items,
  });

  final String attemptId;
  final String testId;
  final String weekId;
  final String difficulty;
  final int ordinal;
  final String status;
  final int questionCount;
  final List<TopicTestChoiceItem> items;

  factory TopicTestAttempt.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(TopicTestChoiceItem.fromJson)
        .toList()
      ..sort((a, b) => a.ordIndex.compareTo(b.ordIndex));
    return TopicTestAttempt(
      attemptId: '${json['attempt_id']}',
      testId: '${json['test_id']}',
      weekId: json['week_id'] as String? ?? '',
      difficulty: json['difficulty'] as String? ?? '',
      ordinal: json['ordinal'] as int? ?? 1,
      status: json['status'] as String? ?? '',
      questionCount: json['question_count'] as int? ?? items.length,
      items: items,
    );
  }
}

class TopicTestReviewItem {
  const TopicTestReviewItem({
    required this.id,
    required this.ordIndex,
    required this.stem,
    required this.choices,
    required this.correctKey,
    this.explanation,
    this.selectedKey,
    this.isCorrect,
  });

  final String id;
  final int ordIndex;
  final String stem;
  final Map<String, String> choices;
  final String correctKey;
  final String? explanation;
  final String? selectedKey;
  final bool? isCorrect;

  factory TopicTestReviewItem.fromJson(Map<String, dynamic> json) {
    final raw = json['choices'];
    final choices = <String, String>{};
    if (raw is Map) {
      for (final e in raw.entries) {
        choices['${e.key}'] = '${e.value}';
      }
    }
    return TopicTestReviewItem(
      id: '${json['id']}',
      ordIndex: json['ord_index'] as int? ?? 0,
      stem: json['stem'] as String? ?? '',
      choices: choices,
      correctKey: json['correct_key'] as String? ?? 'A',
      explanation: json['explanation'] as String?,
      selectedKey: json['selected_key'] as String?,
      isCorrect: json['is_correct'] as bool?,
    );
  }
}

class TopicTestSubmitResult {
  const TopicTestSubmitResult({
    required this.attemptId,
    required this.testId,
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.accuracyPct,
    required this.reviewItems,
  });

  final String attemptId;
  final String testId;
  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final double accuracyPct;
  final List<TopicTestReviewItem> reviewItems;

  factory TopicTestSubmitResult.fromJson(Map<String, dynamic> json) {
    final items = (json['review_items'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(TopicTestReviewItem.fromJson)
        .toList()
      ..sort((a, b) => a.ordIndex.compareTo(b.ordIndex));
    return TopicTestSubmitResult(
      attemptId: '${json['attempt_id']}',
      testId: '${json['test_id']}',
      correctCount: json['correct_count'] as int? ?? 0,
      wrongCount: json['wrong_count'] as int? ?? 0,
      blankCount: json['blank_count'] as int? ?? 0,
      accuracyPct: (json['accuracy_pct'] as num?)?.toDouble() ?? 0,
      reviewItems: items,
    );
  }
}

class TopicTestRemoteDatasource {
  const TopicTestRemoteDatasource(this._dio);

  final Dio _dio;

  Future<TopicTestCatalog> listCatalog({
    required String exam,
    required String subjectCode,
    required String topicCode,
  }) async {
    try {
      final res = await _dio.get(
        ApiEndpoints.topicTestsCatalog,
        queryParameters: {
          'exam': exam,
          'subject_code': subjectCode,
          'topic_code': topicCode,
        },
      );
      final data = res.data['data'] as Map<String, dynamic>? ?? {};
      return TopicTestCatalog.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<TopicTestAttempt> start(String testId) async {
    try {
      final res = await _dio.post(ApiEndpoints.topicTestStart(testId));
      final data = res.data['data'] as Map<String, dynamic>? ?? {};
      return TopicTestAttempt.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    } catch (_) {
      throw const UnknownException(message: 'Test başlatılamadı.');
    }
  }

  Future<TopicTestSubmitResult> submit({
    required String attemptId,
    required Map<String, String?> answers,
  }) async {
    try {
      final payload = {
        'answers': [
          for (final e in answers.entries)
            {
              'item_id': e.key,
              'selected_key': e.value,
            },
        ],
      };
      final res = await _dio.post(
        ApiEndpoints.topicTestSubmit(attemptId),
        data: payload,
      );
      final data = res.data['data'] as Map<String, dynamic>? ?? {};
      return TopicTestSubmitResult.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }
}

final topicTestDatasourceProvider = Provider<TopicTestRemoteDatasource>((ref) {
  return TopicTestRemoteDatasource(ref.watch(dioClientProvider));
});
