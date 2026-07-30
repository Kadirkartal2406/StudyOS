import 'dart:convert';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants/app_config.dart';
import '../features/auth/domain/entities/auth_user.dart';

/// Oturum saklama.
/// - Mobil: refresh + user → secure storage; access → bellek (+ opsiyonel persist)
/// - Web: SharedPreferences (secure storage web'de yenilemede düşüyor)
class LocalStorageService {
  LocalStorageService(this._storage);

  final FlutterSecureStorage _storage;

  String? _accessToken;

  String? get accessToken => _accessToken;

  Future<void> setAccessToken(String token) async {
    _accessToken = token;
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConfig.accessTokenKey, token);
    } else {
      await _storage.write(key: AppConfig.accessTokenKey, value: token);
    }
  }

  void clearAccessToken() {
    _accessToken = null;
  }

  Future<void> restoreAccessToken() async {
    if (_accessToken != null) return;
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      _accessToken = prefs.getString(AppConfig.accessTokenKey);
    } else {
      _accessToken = await _storage.read(key: AppConfig.accessTokenKey);
    }
  }

  Future<void> saveRefreshToken(String token) async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConfig.refreshTokenKey, token);
      return;
    }
    await _storage.write(key: AppConfig.refreshTokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(AppConfig.refreshTokenKey);
    }
    return _storage.read(key: AppConfig.refreshTokenKey);
  }

  Future<void> deleteRefreshToken() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(AppConfig.refreshTokenKey);
      return;
    }
    await _storage.delete(key: AppConfig.refreshTokenKey);
  }

  Future<void> saveUser(AuthUser user) async {
    final raw = jsonEncode(user.toJson());
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConfig.currentUserKey, raw);
      return;
    }
    await _storage.write(key: AppConfig.currentUserKey, value: raw);
  }

  Future<AuthUser?> getUser() async {
    final String? raw;
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      raw = prefs.getString(AppConfig.currentUserKey);
    } else {
      raw = await _storage.read(key: AppConfig.currentUserKey);
    }
    if (raw == null) return null;
    return AuthUser.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  Future<void> deleteUser() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(AppConfig.currentUserKey);
      return;
    }
    await _storage.delete(key: AppConfig.currentUserKey);
  }

  static const firstRunPhaseKey = 'studyos_first_run_phase';

  Future<void> setFirstRunPhase(String phase) async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(firstRunPhaseKey, phase);
      return;
    }
    await _storage.write(key: firstRunPhaseKey, value: phase);
  }

  Future<String?> getFirstRunPhase() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(firstRunPhaseKey);
    }
    return _storage.read(key: firstRunPhaseKey);
  }

  Future<void> clearFirstRunPhase() async {
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(firstRunPhaseKey);
      return;
    }
    await _storage.delete(key: firstRunPhaseKey);
  }

  Future<void> clearAll() async {
    clearAccessToken();
    if (kIsWeb) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(AppConfig.accessTokenKey);
      await prefs.remove(AppConfig.refreshTokenKey);
      await prefs.remove(AppConfig.currentUserKey);
      await prefs.remove(firstRunPhaseKey);
      return;
    }
    await _storage.delete(key: AppConfig.accessTokenKey);
    await deleteRefreshToken();
    await deleteUser();
    await clearFirstRunPhase();
  }

  Future<bool> hasSession() async {
    final token = await getRefreshToken();
    return token != null && token.isNotEmpty;
  }
}

final localStorageServiceProvider = Provider<LocalStorageService>((ref) {
  const storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );
  return LocalStorageService(storage);
});
