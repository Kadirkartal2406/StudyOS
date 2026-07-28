import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/notification_service.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../data/datasources/exam_remote_datasource.dart';
import '../../data/repositories/exam_repository_impl.dart';
import '../../domain/repositories/exam_repository.dart';
import 'exam_state.dart';

final _remoteProvider = Provider<ExamRemoteDatasource>((ref) {
  return ExamRemoteDatasource(ref.watch(dioClientProvider));
});

final examRepositoryProvider = Provider<ExamRepository>((ref) {
  return ExamRepositoryImpl(ref.watch(_remoteProvider));
});

/// J1 — local milestone bildirimleri.
Future<void> notifyExamMilestones(
  NotificationService notifications,
  List<String> milestones,
) async {
  for (final code in milestones) {
    final (title, body) = switch (code) {
      'first_exam' => ('İlk denemen!', 'İlk deneme kaydın oluşturuldu. Devam!'),
      'tenth_exam' => ('10. denemen', '10 deneme tamamladın. Harika istikrar!'),
      'new_record_net' => ('Yeni rekor net', 'Bu denemede net rekorunu kırdın!'),
      _ => (null, null),
    };
    if (title == null || body == null) continue;
    await notifications.show(
      type: AppNotificationType.examMilestone,
      title: title,
      body: body,
    );
  }
}

class ExamNotifier extends StateNotifier<ExamState> {
  ExamNotifier(this._repository, this._notifications, this._ref)
      : super(const ExamInitial()) {
    load();
  }

  final ExamRepository _repository;
  final NotificationService _notifications;
  final Ref _ref;

  String? get _activeExamType =>
      _ref.read(learningProfileProvider).valueOrNull?.activeExamType;

  Future<void> load({String? examType}) async {
    state = const ExamLoading();
    try {
      final scoped = examType ?? _activeExamType;
      final items = await _repository.listExams(examType: scoped);
      final stats = await _repository.getStatistics();
      final trends = await _repository.getTrends();
      state = ExamLoaded(items: items, statistics: stats, trends: trends);
    } on AppException catch (e) {
      state = ExamError(e.message);
    } catch (_) {
      state = const ExamError('Denemeler yüklenemedi');
    }
  }

  Future<bool> create(Map<String, dynamic> body) async {
    try {
      final result = await _repository.createExam(body);
      await notifyExamMilestones(_notifications, result.milestones);
      await load();
      return true;
    } on AppException catch (e) {
      if (state is ExamLoaded) {
        state = ExamLoaded(
          items: (state as ExamLoaded).items,
          statistics: (state as ExamLoaded).statistics,
          trends: (state as ExamLoaded).trends,
          errorMessage: e.message,
        );
      } else {
        state = ExamError(e.message);
      }
      return false;
    } catch (e) {
      if (state is ExamLoaded) {
        state = ExamLoaded(
          items: (state as ExamLoaded).items,
          statistics: (state as ExamLoaded).statistics,
          trends: (state as ExamLoaded).trends,
          errorMessage: 'Deneme kaydı işlenemedi: $e',
        );
      } else {
        state = ExamError('Deneme kaydı işlenemedi');
      }
      return false;
    }
  }

  Future<bool> update(String id, Map<String, dynamic> body) async {
    try {
      await _repository.updateExam(id, body);
      await load();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> replaceResults(
    String id,
    List<Map<String, dynamic>> results,
  ) async {
    try {
      await _repository.replaceResults(id, results);
      await load();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> delete(String id) async {
    try {
      await _repository.deleteExam(id);
      await load();
      return true;
    } catch (_) {
      return false;
    }
  }
}

final examProvider =
    StateNotifierProvider<ExamNotifier, ExamState>((ref) {
  return ExamNotifier(
    ref.watch(examRepositoryProvider),
    ref.watch(appNotificationServiceProvider),
    ref,
  );
});
