import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../constants/api_endpoints.dart';
import '../constants/app_config.dart';
import '../network/dio_client.dart';

/// Sprint 21 RC.7 — Merkezi analytics (fire-and-forget).
class AnalyticsService {
  AnalyticsService(this._dio);

  final Dio _dio;
  final String sessionId =
      's_${DateTime.now().millisecondsSinceEpoch}';

  Future<void> track(
    String name, {
    Map<String, dynamic>? properties,
  }) async {
    try {
      await _dio.post(
        ApiEndpoints.analyticsTrack,
        data: {
          'name': name,
          'platform': defaultTargetPlatform.name,
          'app_version': AppConfig.appVersion,
          'session_id': sessionId,
          'properties': properties ?? {},
        },
      );
    } catch (_) {
      // Analytics UI'yi bozmaz
    }
  }

  void trackSync(String name, {Map<String, dynamic>? properties}) {
    unawaited(track(name, properties: properties));
  }
}

final analyticsServiceProvider = Provider<AnalyticsService>((ref) {
  return AnalyticsService(ref.watch(dioClientProvider));
});

/// Standart event isimleri (backend AnalyticsEventName ile hizalı).
abstract final class AnalyticsEvents {
  static const appOpen = 'app_open';
  static const todayViewed = 'today_viewed';
  static const topicOpened = 'topic_opened';
  static const quizGenerated = 'quiz_generated';
  static const quizFinished = 'quiz_finished';
  static const assessmentStarted = 'assessment_started';
  static const assessmentFinished = 'assessment_finished';
  static const explainUsed = 'explain_used';
  static const coachViewed = 'coach_viewed';
  static const notebookViewed = 'notebook_viewed';
  static const resourceAdded = 'resource_added';
  static const feedbackSent = 'feedback_sent';
  static const errorReported = 'error_reported';
}
