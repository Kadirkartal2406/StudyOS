import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ThemePreferences {
  const ThemePreferences({
    this.mode = ThemeMode.system,
    this.accent = const Color(0xFF0D9488),
  });

  final ThemeMode mode;
  final Color accent;

  ThemePreferences copyWith({ThemeMode? mode, Color? accent}) =>
      ThemePreferences(
        mode: mode ?? this.mode,
        accent: accent ?? this.accent,
      );

  static const accentOptions = <Color>[
    Color(0xFF0D9488), // teal
    Color(0xFF2563EB), // blue
    Color(0xFF7C3AED), // purple
    Color(0xFFEA580C), // orange
    Color(0xFFDC2626), // red
    Color(0xFF16A34A), // green
  ];
}

class ThemePreferencesNotifier extends StateNotifier<ThemePreferences> {
  ThemePreferencesNotifier() : super(const ThemePreferences()) {
    _load();
  }

  static const _modeKey = 'studyos_theme_mode';
  static const _accentKey = 'studyos_accent';
  final _storage = const FlutterSecureStorage();

  Future<void> _load() async {
    final modeRaw = await _storage.read(key: _modeKey);
    final accentRaw = await _storage.read(key: _accentKey);
    var mode = ThemeMode.system;
    if (modeRaw == 'light') mode = ThemeMode.light;
    if (modeRaw == 'dark') mode = ThemeMode.dark;
    Color accent = ThemePreferences.accentOptions.first;
    if (accentRaw != null) {
      final v = int.tryParse(accentRaw);
      if (v != null) accent = Color(v);
    }
    state = ThemePreferences(mode: mode, accent: accent);
  }

  Future<void> setMode(ThemeMode mode) async {
    state = state.copyWith(mode: mode);
    final raw = switch (mode) {
      ThemeMode.light => 'light',
      ThemeMode.dark => 'dark',
      ThemeMode.system => 'system',
    };
    await _storage.write(key: _modeKey, value: raw);
  }

  Future<void> setAccent(Color accent) async {
    state = state.copyWith(accent: accent);
    await _storage.write(key: _accentKey, value: accent.toARGB32().toString());
  }
}

final themePreferencesProvider =
    StateNotifierProvider<ThemePreferencesNotifier, ThemePreferences>((ref) {
  return ThemePreferencesNotifier();
});
