import '../../domain/entities/study_session_entity.dart';

sealed class SessionHistoryState {
  const SessionHistoryState();
}

class SessionHistoryInitial extends SessionHistoryState {
  const SessionHistoryInitial();
}

class SessionHistoryLoading extends SessionHistoryState {
  const SessionHistoryLoading();
}

class SessionHistoryLoaded extends SessionHistoryState {
  const SessionHistoryLoaded({
    required this.items,
    required this.hasMore,
    required this.isLoadingMore,
    this.statusFilter,
    this.searchQuery,
    this.dateFrom,
    this.dateTo,
    this.errorMessage,
  });

  final List<StudySessionEntity> items;
  final bool hasMore;
  final bool isLoadingMore;
  final String? statusFilter;
  final String? searchQuery;
  final DateTime? dateFrom;
  final DateTime? dateTo;
  final String? errorMessage;

  SessionHistoryLoaded copyWith({
    List<StudySessionEntity>? items,
    bool? hasMore,
    bool? isLoadingMore,
    String? statusFilter,
    String? searchQuery,
    DateTime? dateFrom,
    DateTime? dateTo,
    String? errorMessage,
    bool clearError = false,
  }) {
    return SessionHistoryLoaded(
      items: items ?? this.items,
      hasMore: hasMore ?? this.hasMore,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
      statusFilter: statusFilter ?? this.statusFilter,
      searchQuery: searchQuery ?? this.searchQuery,
      dateFrom: dateFrom ?? this.dateFrom,
      dateTo: dateTo ?? this.dateTo,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class SessionHistoryError extends SessionHistoryState {
  const SessionHistoryError(this.message);
  final String message;
}
