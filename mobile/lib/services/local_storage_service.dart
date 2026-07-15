import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../core/constants/app_config.dart';
import '../features/auth/domain/entities/auth_user.dart';

/// flutter_secure_storage wrapper.
/// Access token in-memory (kısa ömürlü, 15 dk), refresh token secure storage'da.
class LocalStorageService {
  LocalStorageService(this._storage);

  final FlutterSecureStorage _storage;

  // ── Access Token (in-memory) ──────────────────────────────
  String? _accessToken;

  String? get accessToken => _accessToken;

  void setAccessToken(String token) => _accessToken = token;

  void clearAccessToken() => _accessToken = null;

  // ── Refresh Token (secure storage) ───────────────────────
  Future<void> saveRefreshToken(String token) =>
      _storage.write(key: AppConfig.refreshTokenKey, value: token);

  Future<String?> getRefreshToken() =>
      _storage.read(key: AppConfig.refreshTokenKey);

  Future<void> deleteRefreshToken() =>
      _storage.delete(key: AppConfig.refreshTokenKey);

  // ── Current User (secure storage) ────────────────────────
  Future<void> saveUser(AuthUser user) => _storage.write(
        key: AppConfig.currentUserKey,
        value: jsonEncode(user.toJson()),
      );

  Future<AuthUser?> getUser() async {
    final raw = await _storage.read(key: AppConfig.currentUserKey);
    if (raw == null) return null;
    return AuthUser.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  Future<void> deleteUser() =>
      _storage.delete(key: AppConfig.currentUserKey);

  // ── Oturum Temizleme ──────────────────────────────────────
  Future<void> clearAll() async {
    clearAccessToken();
    await deleteRefreshToken();
    await deleteUser();
  }

  Future<bool> hasSession() async {
    final token = await getRefreshToken();
    return token != null;
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
