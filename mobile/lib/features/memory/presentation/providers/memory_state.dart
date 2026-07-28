import '../../domain/entities/memory_entity.dart';

sealed class MemoryState {
  const MemoryState();
}

class MemoryInitial extends MemoryState {
  const MemoryInitial();
}

class MemoryLoading extends MemoryState {
  const MemoryLoading();
}

class MemoryLoaded extends MemoryState {
  const MemoryLoaded({
    required this.items,
    required this.aiMemoryEnabled,
    this.query = '',
    this.errorMessage,
    this.infoMessage,
  });

  final List<MemoryEntity> items;
  final bool aiMemoryEnabled;
  final String query;
  final String? errorMessage;
  final String? infoMessage;

  MemoryLoaded copyWith({
    List<MemoryEntity>? items,
    bool? aiMemoryEnabled,
    String? query,
    String? errorMessage,
    String? infoMessage,
    bool clearError = false,
    bool clearInfo = false,
  }) {
    return MemoryLoaded(
      items: items ?? this.items,
      aiMemoryEnabled: aiMemoryEnabled ?? this.aiMemoryEnabled,
      query: query ?? this.query,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
      infoMessage: clearInfo ? null : (infoMessage ?? this.infoMessage),
    );
  }
}

class MemoryError extends MemoryState {
  const MemoryError(this.message);

  final String message;
}
