import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../domain/entities/study_session_entity.dart';
import '../../domain/repositories/study_session_repository.dart';
import 'session_history_state.dart';
import 'study_session_provider.dart';

class SessionHistoryNotifier extends StateNotifier<SessionHistoryState> {
  SessionHistoryNotifier(this._repo) : super(const SessionHistoryInitial()) {
    load();
  }

  final StudySessionRepository _repo;
  int _page = 1;
  static const _pageSize = 20;

  Future<void> load({
    String? statusFilter,
    String? searchQuery,
    DateTime? dateFrom,
    DateTime? dateTo,
  }) async {
    state = const SessionHistoryLoading();
    _page = 1;
    try {
      final StudySessionHistoryResult result = await _repo.getHistory(
        page: _page,
        pageSize: _pageSize,
        status: statusFilter,
        q: searchQuery,
        dateFrom: dateFrom,
        dateTo: dateTo,
      );
      state = SessionHistoryLoaded(
        items: result.items,
        hasMore: result.hasMore,
        isLoadingMore: false,
        statusFilter: statusFilter,
        searchQuery: searchQuery,
        dateFrom: dateFrom,
        dateTo: dateTo,
      );
    } on AppException catch (e) {
      state = SessionHistoryError(e.message);
    } catch (_) {
      state = const SessionHistoryError('Geçmiş yüklenemedi');
    }
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is! SessionHistoryLoaded ||
        !current.hasMore ||
        current.isLoadingMore) {
      return;
    }
    state = current.copyWith(isLoadingMore: true);
    try {
      final nextPage = _page + 1;
      final result = await _repo.getHistory(
        page: nextPage,
        pageSize: _pageSize,
        status: current.statusFilter,
        q: current.searchQuery,
        dateFrom: current.dateFrom,
        dateTo: current.dateTo,
      );
      _page = nextPage;
      state = current.copyWith(
        items: [...current.items, ...result.items],
        hasMore: result.hasMore,
        isLoadingMore: false,
      );
    } on AppException catch (e) {
      state = current.copyWith(isLoadingMore: false, errorMessage: e.message);
    } catch (_) {
      state = current.copyWith(
        isLoadingMore: false,
        errorMessage: 'Daha fazla yüklenemedi',
      );
    }
  }

  Future<void> applyFilters({
    String? statusFilter,
    String? searchQuery,
    DateTime? dateFrom,
    DateTime? dateTo,
  }) {
    return load(
      statusFilter: statusFilter,
      searchQuery: searchQuery,
      dateFrom: dateFrom,
      dateTo: dateTo,
    );
  }
}

final sessionHistoryProvider =
    StateNotifierProvider<SessionHistoryNotifier, SessionHistoryState>((ref) {
  return SessionHistoryNotifier(ref.watch(studySessionRepositoryProvider));
});
