import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../services/local_storage_service.dart';

/// RC3 — sohbet sonrası kurulum fazı (motor değil, UX gate).
/// null = henüz yüklenmedi; 'done' veya yok = setup bitti.
class FirstRunPhaseNotifier extends StateNotifier<String?> {
  FirstRunPhaseNotifier(this._storage) : super(null) {
    refresh();
  }

  final LocalStorageService _storage;

  Future<void> refresh() async {
    state = await _storage.getFirstRunPhase();
  }

  Future<void> setPhase(String phase) async {
    await _storage.setFirstRunPhase(phase);
    state = phase;
  }

  Future<void> clear() async {
    await _storage.clearFirstRunPhase();
    state = null;
  }

  bool get isSetupPending {
    final p = state;
    if (p == null || p.isEmpty || p == 'done') return false;
    return true;
  }

  String? get setupRoute {
    switch (state) {
      case 'wow':
        return '/setup/wow';
      case 'calibration':
      case 'calibration_active':
        return '/setup/calibration';
      case 'preparing':
        return '/setup/preparing';
      case 'system_summary':
        return '/setup/system-summary';
      case 'today_plan':
        return '/setup/today-plan';
      case 'tour':
        return '/setup/tour';
      default:
        return null;
    }
  }
}

final firstRunPhaseProvider =
    StateNotifierProvider<FirstRunPhaseNotifier, String?>((ref) {
  return FirstRunPhaseNotifier(ref.watch(localStorageServiceProvider));
});
