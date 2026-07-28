import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/ai_settings_remote_datasource.dart';
import '../../data/models/ai_settings_model.dart';

final _aiSettingsRemoteProvider = Provider<AiSettingsRemoteDatasource>((ref) {
  return AiSettingsRemoteDatasource(ref.watch(dioClientProvider));
});

sealed class AiSettingsState {
  const AiSettingsState();
}

class AiSettingsLoading extends AiSettingsState {
  const AiSettingsLoading();
}

class AiSettingsLoaded extends AiSettingsState {
  const AiSettingsLoaded(this.settings, {this.errorMessage});

  final AiSettingsModel settings;
  final String? errorMessage;
}

class AiSettingsError extends AiSettingsState {
  const AiSettingsError(this.message);

  final String message;
}

class AiSettingsNotifier extends StateNotifier<AiSettingsState> {
  AiSettingsNotifier(this._remote) : super(const AiSettingsLoading()) {
    load();
  }

  final AiSettingsRemoteDatasource _remote;

  Future<void> load() async {
    state = const AiSettingsLoading();
    try {
      final settings = await _remote.getSettings();
      state = AiSettingsLoaded(settings);
    } on AppException catch (e) {
      state = AiSettingsError(e.message);
    } catch (_) {
      state = const AiSettingsError('AI ayarları yüklenemedi');
    }
  }

  Future<void> setProvider(String provider) async {
    final current = state;
    if (current is! AiSettingsLoaded) return;
    try {
      final settings = await _remote.updateSettings(preferredProvider: provider);
      state = AiSettingsLoaded(settings);
    } on AppException catch (e) {
      state = AiSettingsLoaded(current.settings, errorMessage: e.message);
    }
  }

  Future<void> setModel(String model) async {
    final current = state;
    if (current is! AiSettingsLoaded) return;
    try {
      final settings =
          await _remote.updateSettings(preferredModel: model.trim());
      state = AiSettingsLoaded(settings);
    } on AppException catch (e) {
      state = AiSettingsLoaded(current.settings, errorMessage: e.message);
    }
  }
}

final aiSettingsProvider =
    StateNotifierProvider<AiSettingsNotifier, AiSettingsState>((ref) {
  return AiSettingsNotifier(ref.watch(_aiSettingsRemoteProvider));
});
