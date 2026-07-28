import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/memory_remote_datasource.dart';
import '../../data/repositories/memory_repository_impl.dart';
import '../../domain/entities/memory_entity.dart';
import '../../domain/repositories/memory_repository.dart';
import 'memory_state.dart';

final _remoteProvider = Provider<MemoryRemoteDatasource>((ref) {
  return MemoryRemoteDatasource(ref.watch(dioClientProvider));
});

final memoryRepositoryProvider = Provider<MemoryRepository>((ref) {
  return MemoryRepositoryImpl(ref.watch(_remoteProvider));
});

class MemoryNotifier extends StateNotifier<MemoryState> {
  MemoryNotifier(this._repository) : super(const MemoryInitial()) {
    load();
  }

  final MemoryRepository _repository;

  Future<void> load() async {
    state = const MemoryLoading();
    try {
      final items = await _repository.listMemories();
      final settings = await _repository.getSettings();
      state = MemoryLoaded(
        items: items,
        aiMemoryEnabled: settings.aiMemoryEnabled,
      );
    } on AppException catch (e) {
      state = MemoryError(e.message);
    } catch (_) {
      state = const MemoryError('Bellekler yüklenemedi');
    }
  }

  Future<void> search(String query) async {
    final current = state;
    if (current is! MemoryLoaded) return;
    try {
      final items = query.trim().isEmpty
          ? await _repository.listMemories()
          : await _repository.search(query: query.trim());
      state = current.copyWith(items: items, query: query, clearError: true);
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }

  Future<bool> create({
    required MemoryCategory category,
    required String content,
    double importance = 0.5,
  }) async {
    final current = state;
    try {
      await _repository.createMemory(
        category: category,
        content: content,
        importance: importance,
      );
      await load();
      return true;
    } on AppException catch (e) {
      if (current is MemoryLoaded) {
        state = current.copyWith(errorMessage: e.message);
      } else {
        state = MemoryError(e.message);
      }
      return false;
    }
  }

  Future<bool> update({
    required String id,
    MemoryCategory? category,
    String? content,
    double? importance,
  }) async {
    final current = state;
    try {
      await _repository.updateMemory(
        id: id,
        category: category,
        content: content,
        importance: importance,
      );
      await load();
      return true;
    } on AppException catch (e) {
      if (current is MemoryLoaded) {
        state = current.copyWith(errorMessage: e.message);
      }
      return false;
    }
  }

  Future<void> delete(String id) async {
    final current = state;
    if (current is! MemoryLoaded) return;
    try {
      await _repository.deleteMemory(id);
      state = current.copyWith(
        items: current.items.where((e) => e.id != id).toList(),
        clearError: true,
      );
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }

  Future<void> setEnabled(bool enabled) async {
    final current = state;
    if (current is! MemoryLoaded) return;
    try {
      final settings = await _repository.updateSettings(enabled: enabled);
      state = current.copyWith(
        aiMemoryEnabled: settings.aiMemoryEnabled,
        infoMessage: enabled ? 'AI bellek açık' : 'AI bellek kapalı',
        clearError: true,
      );
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }

  Future<void> clearAll() async {
    final current = state;
    if (current is! MemoryLoaded) return;
    try {
      final deleted = await _repository.clearMemories();
      state = current.copyWith(
        items: const [],
        infoMessage: '$deleted bellek silindi',
        clearError: true,
      );
    } on AppException catch (e) {
      state = current.copyWith(errorMessage: e.message);
    }
  }

  Future<String?> exportSummary() async {
    final current = state;
    try {
      final items = await _repository.exportMemories();
      if (current is MemoryLoaded) {
        state = current.copyWith(
          infoMessage: '${items.length} bellek dışa aktarıldı',
          clearError: true,
        );
      }
      return items.map((e) => '[${e.category.label}] ${e.content}').join('\n');
    } on AppException catch (e) {
      if (current is MemoryLoaded) {
        state = current.copyWith(errorMessage: e.message);
      }
      return null;
    }
  }
}

final memoryProvider =
    StateNotifierProvider<MemoryNotifier, MemoryState>((ref) {
  return MemoryNotifier(ref.watch(memoryRepositoryProvider));
});
