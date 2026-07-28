import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/app_exception.dart';
import '../../../core/errors/dio_exception_mapper.dart';
import '../../../core/network/dio_client.dart';

class QuizChoiceItem {
  const QuizChoiceItem({
    required this.id,
    required this.ordIndex,
    required this.stem,
    required this.choices,
  });

  final String id;
  final int ordIndex;
  final String stem;
  final Map<String, String> choices;

  factory QuizChoiceItem.fromJson(Map<String, dynamic> json) {
    final raw = json['choices'];
    final choices = <String, String>{};
    if (raw is Map) {
      for (final e in raw.entries) {
        choices['${e.key}'] = '${e.value}';
      }
    }
    return QuizChoiceItem(
      id: '${json["id"]}',
      ordIndex: json['ord_index'] as int? ?? 0,
      stem: json['stem'] as String? ?? '',
      choices: choices,
    );
  }
}

class QuizGenerationEntity {
  const QuizGenerationEntity({
    required this.id,
    required this.subjectCode,
    required this.topicCode,
    required this.status,
    required this.items,
    this.subjectName,
    this.topicName,
    this.validItemCount = 0,
  });

  final String id;
  final String subjectCode;
  final String topicCode;
  final String? subjectName;
  final String? topicName;
  final String status;
  final int validItemCount;
  final List<QuizChoiceItem> items;

  factory QuizGenerationEntity.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(QuizChoiceItem.fromJson)
        .toList()
      ..sort((a, b) => a.ordIndex.compareTo(b.ordIndex));
    return QuizGenerationEntity(
      id: '${json["id"]}',
      subjectCode: json['subject_code'] as String? ?? '',
      topicCode: json['topic_code'] as String? ?? '',
      subjectName: json['subject_name'] as String?,
      topicName: json['topic_name'] as String?,
      status: json['status'] as String? ?? '',
      validItemCount: json['valid_item_count'] as int? ?? items.length,
      items: items,
    );
  }
}

class QuizReviewItem {
  const QuizReviewItem({
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

  factory QuizReviewItem.fromJson(Map<String, dynamic> json) {
    final raw = json['choices'];
    final choices = <String, String>{};
    if (raw is Map) {
      for (final e in raw.entries) {
        choices['${e.key}'] = '${e.value}';
      }
    }
    return QuizReviewItem(
      id: '${json["id"]}',
      ordIndex: json['ord_index'] as int? ?? 0,
      stem: json['stem'] as String? ?? '',
      choices: choices,
      correctKey: json['correct_key'] as String? ?? '',
      explanation: json['explanation'] as String?,
      selectedKey: json['selected_key'] as String?,
      isCorrect: json['is_correct'] as bool?,
    );
  }
}

class QuizSubmitResultEntity {
  const QuizSubmitResultEntity({
    required this.correctCount,
    required this.wrongCount,
    required this.blankCount,
    required this.accuracyPct,
    required this.reviewItems,
  });

  final int correctCount;
  final int wrongCount;
  final int blankCount;
  final double accuracyPct;
  final List<QuizReviewItem> reviewItems;

  factory QuizSubmitResultEntity.fromJson(Map<String, dynamic> json) {
    final reviews = (json['review_items'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(QuizReviewItem.fromJson)
        .toList()
      ..sort((a, b) => a.ordIndex.compareTo(b.ordIndex));
    return QuizSubmitResultEntity(
      correctCount: json['correct_count'] as int? ?? 0,
      wrongCount: json['wrong_count'] as int? ?? 0,
      blankCount: json['blank_count'] as int? ?? 0,
      accuracyPct: (json['accuracy_pct'] as num?)?.toDouble() ?? 0,
      reviewItems: reviews,
    );
  }
}

class TopicQuizRemoteDatasource {
  const TopicQuizRemoteDatasource(this._dio);

  final Dio _dio;

  Future<QuizGenerationEntity> generate({
    required String subjectCode,
    required String topicCode,
    int count = 5,
    String difficulty = 'medium',
    String? examType,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.topicQuizSessionGenerate(subjectCode, topicCode),
        data: {
          'count': count,
          'difficulty': difficulty,
          if (examType != null && examType.isNotEmpty) 'exam_type': examType,
        },
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Geçersiz quiz üretim yanıtı');
      }
      return QuizGenerationEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<QuizGenerationEntity> get(String generationId) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.topicQuizSession(generationId),
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Geçersiz quiz yanıtı');
      }
      return QuizGenerationEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<QuizSubmitResultEntity> submit({
    required String generationId,
    required Map<String, String?> answers,
  }) async {
    try {
      final payload = {
        'answers': answers.entries
            .map((e) => {'item_id': e.key, 'selected_key': e.value})
            .toList(),
      };
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.topicQuizSessionSubmit(generationId),
        data: payload,
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Geçersiz quiz sonuç yanıtı');
      }
      return QuizSubmitResultEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }
}

final topicQuizDatasourceProvider = Provider<TopicQuizRemoteDatasource>((ref) {
  return TopicQuizRemoteDatasource(ref.watch(dioClientProvider));
});
