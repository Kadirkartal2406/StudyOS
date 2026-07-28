import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../data/datasources/question_tracking_remote_datasource.dart';
import '../../data/repositories/question_tracking_repository_impl.dart';
import '../../domain/entities/question_enums.dart';
import '../../domain/entities/question_record_entity.dart';
import '../../domain/repositories/question_tracking_repository.dart';
import '../../domain/usecases/question_tracking_usecases.dart';
import 'question_tracking_state.dart';

final questionTrackingRepositoryProvider =
    Provider<QuestionTrackingRepository>((ref) {
  return QuestionTrackingRepositoryImpl(
    QuestionTrackingRemoteDatasource(ref.watch(dioClientProvider)),
  );
});

final questionListProvider =
    StateNotifierProvider<QuestionListNotifier, QuestionListState>((ref) {
  final repo = ref.watch(questionTrackingRepositoryProvider);
  return QuestionListNotifier(
    GetQuestionsUsecase(repo),
    DeleteQuestionUsecase(repo),
    ref,
  );
});

class QuestionListNotifier extends StateNotifier<QuestionListState> {
  QuestionListNotifier(this._getList, this._delete, this._ref)
      : super(const QuestionListInitial()) {
    load();
  }

  final GetQuestionsUsecase _getList;
  final DeleteQuestionUsecase _delete;
  final Ref _ref;

  Future<void> load({String? subject, ExamType? examType}) async {
    state = const QuestionListLoading();
    try {
      final scoped = examType ??
          ExamType.fromApi(
            _ref.read(learningProfileProvider).valueOrNull?.activeExamType,
          );
      final page = await _getList(subject: subject, examType: scoped);
      state = QuestionListLoaded(page);
    } on AppException catch (e) {
      state = QuestionListError(e.message);
    } catch (_) {
      state = const QuestionListError('Soru kayıtları yüklenemedi');
    }
  }

  Future<void> delete(String id) async {
    await _delete(id);
    await load();
  }
}

class QuestionMutationFacade {
  const QuestionMutationFacade({
    required this.create,
    required this.update,
    required this.getById,
  });

  final CreateQuestionUsecase create;
  final UpdateQuestionUsecase update;
  final GetQuestionByIdUsecase getById;
}

final questionMutationProvider = Provider<QuestionMutationFacade>((ref) {
  final repo = ref.watch(questionTrackingRepositoryProvider);
  return QuestionMutationFacade(
    create: CreateQuestionUsecase(repo),
    update: UpdateQuestionUsecase(repo),
    getById: GetQuestionByIdUsecase(repo),
  );
});

final questionDetailProvider =
    FutureProvider.family<QuestionRecordEntity, String>((ref, id) async {
  return ref.watch(questionMutationProvider).getById(id);
});

final questionStatsProvider =
    StateNotifierProvider<QuestionStatsNotifier, QuestionStatsState>((ref) {
  final repo = ref.watch(questionTrackingRepositoryProvider);
  return QuestionStatsNotifier(
    GetQuestionStatisticsUsecase(repo),
    GetQuestionDailyUsecase(repo),
    GetQuestionSubjectsUsecase(repo),
    GetQuestionTopicsUsecase(repo),
    GetQuestionExamsUsecase(repo),
  );
});

class QuestionStatsNotifier extends StateNotifier<QuestionStatsState> {
  QuestionStatsNotifier(
    this._overview,
    this._daily,
    this._subjects,
    this._topics,
    this._exams,
  ) : super(const QuestionStatsInitial()) {
    load();
  }

  final GetQuestionStatisticsUsecase _overview;
  final GetQuestionDailyUsecase _daily;
  final GetQuestionSubjectsUsecase _subjects;
  final GetQuestionTopicsUsecase _topics;
  final GetQuestionExamsUsecase _exams;

  Future<void> load() async {
    state = const QuestionStatsLoading();
    try {
      final overview = await _overview();
      final daily = await _daily();
      final subjects = await _subjects();
      final topics = await _topics();
      final exams = await _exams();
      state = QuestionStatsLoaded(
        overview: overview,
        daily: daily,
        subjects: subjects,
        topics: topics,
        exams: exams,
      );
    } on AppException catch (e) {
      state = QuestionStatsError(e.message);
    } catch (_) {
      state = const QuestionStatsError('Soru istatistikleri yüklenemedi');
    }
  }
}
