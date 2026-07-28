import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/study_plan_remote_datasource.dart';
import '../../data/repositories/study_plan_repository_impl.dart';
import '../../domain/entities/study_plan_entity.dart';
import '../../domain/entities/study_time.dart';
import '../../domain/repositories/study_plan_repository.dart';
import '../../domain/usecases/complete_study_plan_usecase.dart';
import '../../domain/usecases/create_study_plan_usecase.dart';
import '../../domain/usecases/delete_study_plan_usecase.dart';
import '../../domain/usecases/get_study_plans_usecase.dart';
import '../../domain/usecases/reorder_study_plan_usecase.dart';
import '../../domain/usecases/skip_study_plan_usecase.dart';
import '../../domain/usecases/start_study_plan_usecase.dart';
import '../../domain/usecases/update_study_plan_usecase.dart';
import 'study_plan_state.dart';

// ── Dependency Injection ────────────────────────────────────────────────────

final _remoteDatasourceProvider = Provider<StudyPlanRemoteDatasource>((ref) {
  return StudyPlanRemoteDatasource(ref.watch(dioClientProvider));
});

final studyPlanRepositoryProvider = Provider<StudyPlanRepository>((ref) {
  return StudyPlanRepositoryImpl(ref.watch(_remoteDatasourceProvider));
});

final _getStudyPlansProvider = Provider<GetStudyPlansUsecase>((ref) {
  return GetStudyPlansUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _createStudyPlanProvider = Provider<CreateStudyPlanUsecase>((ref) {
  return CreateStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _updateStudyPlanProvider = Provider<UpdateStudyPlanUsecase>((ref) {
  return UpdateStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _deleteStudyPlanProvider = Provider<DeleteStudyPlanUsecase>((ref) {
  return DeleteStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _startStudyPlanProvider = Provider<StartStudyPlanUsecase>((ref) {
  return StartStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _completeStudyPlanProvider = Provider<CompleteStudyPlanUsecase>((ref) {
  return CompleteStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _skipStudyPlanProvider = Provider<SkipStudyPlanUsecase>((ref) {
  return SkipStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

final _reorderStudyPlanProvider = Provider<ReorderStudyPlanUsecase>((ref) {
  return ReorderStudyPlanUsecase(ref.watch(studyPlanRepositoryProvider));
});

// ── StudyPlan Notifier ───────────────────────────────────────────────────────

/// Çalışma planı listesi ve tekil plan işlemlerini (CRUD + durum geçişi +
/// sıralama) yöneten Riverpod StateNotifier.
class StudyPlanNotifier extends StateNotifier<StudyPlanState> {
  StudyPlanNotifier({
    required GetStudyPlansUsecase getPlans,
    required StudyPlanRepository repository,
    required CreateStudyPlanUsecase createPlan,
    required UpdateStudyPlanUsecase updatePlan,
    required DeleteStudyPlanUsecase deletePlan,
    required StartStudyPlanUsecase startPlan,
    required CompleteStudyPlanUsecase completePlan,
    required SkipStudyPlanUsecase skipPlan,
    required ReorderStudyPlanUsecase reorderPlan,
  })  : _getPlans = getPlans,
        _repository = repository,
        _createPlan = createPlan,
        _updatePlan = updatePlan,
        _deletePlan = deletePlan,
        _startPlan = startPlan,
        _completePlan = completePlan,
        _skipPlan = skipPlan,
        _reorderPlan = reorderPlan,
        super(const StudyPlanInitial()) {
    load(DateTime.now());
  }

  final GetStudyPlansUsecase _getPlans;
  final StudyPlanRepository _repository;
  final CreateStudyPlanUsecase _createPlan;
  final UpdateStudyPlanUsecase _updatePlan;
  final DeleteStudyPlanUsecase _deletePlan;
  final StartStudyPlanUsecase _startPlan;
  final CompleteStudyPlanUsecase _completePlan;
  final SkipStudyPlanUsecase _skipPlan;
  final ReorderStudyPlanUsecase _reorderPlan;

  static DateTime _normalize(DateTime date) =>
      DateTime(date.year, date.month, date.day);

  DateTime get _currentDate => switch (state) {
        StudyPlanLoaded(:final selectedDate) => selectedDate,
        StudyPlanLoading(:final selectedDate) => selectedDate,
        StudyPlanError(:final selectedDate) => selectedDate,
        StudyPlanInitial() => _normalize(DateTime.now()),
      };

  /// Belirtilen güne ait planları backend'den yükler.
  Future<void> load(DateTime date) async {
    final normalized = _normalize(date);
    state = StudyPlanLoading(normalized);
    try {
      final plans = await _getPlans(normalized);
      state = StudyPlanLoaded(selectedDate: normalized, plans: plans);
    } on AppException catch (e) {
      state = StudyPlanError(normalized, e.message);
    } catch (_) {
      state = StudyPlanError(normalized, 'Beklenmeyen bir hata oluştu');
    }
  }

  /// Gün seçiciden gelen tarih değişikliğini uygular.
  Future<void> changeDate(DateTime date) => load(date);

  /// "Bugün" butonu.
  Future<void> goToToday() => load(DateTime.now());

  /// Hata durumunda tekrar dene.
  Future<void> retry() => load(_currentDate);

  /// Yeni plan oluşturur; başarılıysa listeyi yeniler.
  Future<void> createPlan({
    required String title,
    required String subject,
    String? topic,
    required int targetQuestionCount,
    required int estimatedMinutes,
    StudyTime? plannedStartTime,
    StudyTime? plannedEndTime,
  }) async {
    final date = _currentDate;
    await _createPlan(
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      studyDate: date,
      plannedStartTime: plannedStartTime,
      plannedEndTime: plannedEndTime,
    );
    await load(date);
  }

  /// Mevcut planı günceller; başarılıysa listeyi yeniler.
  Future<void> updatePlan({
    required String id,
    required String title,
    required String subject,
    String? topic,
    required int targetQuestionCount,
    required int estimatedMinutes,
    StudyTime? plannedStartTime,
    StudyTime? plannedEndTime,
    DateTime? studyDate,
  }) async {
    final date = studyDate != null ? _normalize(studyDate) : _currentDate;
    await _updatePlan(
      id: id,
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      studyDate: date,
      plannedStartTime: plannedStartTime,
      plannedEndTime: plannedEndTime,
    );
    await load(date);
  }

  /// Tek planı id ile getir (düzenleme ekranı için).
  Future<StudyPlanEntity?> fetchPlanById(String id) async {
    try {
      return await _repository.getPlan(id);
    } catch (_) {
      return null;
    }
  }

  Future<void> deletePlan(String id) => _mutate(id, () => _deletePlan(id));

  Future<void> startPlan(String id) => _mutate(id, () async => _startPlan(id));

  Future<void> completePlan(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  }) {
    return _mutate(
      id,
      () async => _completePlan(
        id,
        completedQuestionCount: completedQuestionCount,
        completedMinutes: completedMinutes,
      ),
    );
  }

  Future<void> skipPlan(String id) => _mutate(id, () async => _skipPlan(id));

  /// Drag & Drop sonrası yeni sıralamayı yerel olarak uygular ve
  /// değişen `order_index` değerlerini backend'e kaydeder.
  Future<void> reorder(int oldIndex, int newIndex) async {
    final current = state;
    if (current is! StudyPlanLoaded) return;

    final plans = [...current.plans];
    var targetIndex = newIndex;
    if (targetIndex > oldIndex) targetIndex -= 1;
    final moved = plans.removeAt(oldIndex);
    plans.insert(targetIndex, moved);

    final reindexed = <StudyPlanEntity>[];
    final changed = <StudyPlanEntity>[];
    for (var i = 0; i < plans.length; i++) {
      final plan = plans[i];
      if (plan.orderIndex != i) {
        final updated = plan.copyWith(orderIndex: i);
        reindexed.add(updated);
        changed.add(updated);
      } else {
        reindexed.add(plan);
      }
    }

    state = current.copyWith(plans: reindexed);

    try {
      for (final plan in changed) {
        await _reorderPlan(plan, plan.orderIndex);
      }
    } on AppException {
      await load(current.selectedDate);
      rethrow;
    }
  }

  Future<void> _mutate(String id, Future<void> Function() action) async {
    final current = state;
    if (current is! StudyPlanLoaded) return;

    state = current.copyWith(mutatingPlanId: id);
    try {
      await action();
      await load(current.selectedDate);
    } on AppException {
      state = current.copyWith(clearMutatingPlanId: true);
      rethrow;
    }
  }
}

// ── Provider ─────────────────────────────────────────────────────────────────

final studyPlanProvider =
    StateNotifierProvider<StudyPlanNotifier, StudyPlanState>((ref) {
  return StudyPlanNotifier(
    getPlans: ref.watch(_getStudyPlansProvider),
    repository: ref.watch(studyPlanRepositoryProvider),
    createPlan: ref.watch(_createStudyPlanProvider),
    updatePlan: ref.watch(_updateStudyPlanProvider),
    deletePlan: ref.watch(_deleteStudyPlanProvider),
    startPlan: ref.watch(_startStudyPlanProvider),
    completePlan: ref.watch(_completeStudyPlanProvider),
    skipPlan: ref.watch(_skipStudyPlanProvider),
    reorderPlan: ref.watch(_reorderStudyPlanProvider),
  );
});
