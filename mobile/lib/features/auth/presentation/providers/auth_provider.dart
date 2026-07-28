import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../services/local_storage_service.dart';
import '../../data/datasources/remote_auth_datasource.dart';
import '../../data/repositories/auth_repository_impl.dart';
import '../../domain/repositories/auth_repository.dart';
import 'auth_state.dart';

// ── Dependency Injection ──────────────────────────────────────────────────────

final _remoteDatasourceProvider = Provider<RemoteAuthDatasource>((ref) {
  return RemoteAuthDatasource(ref.watch(dioClientProvider));
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(ref.watch(_remoteDatasourceProvider));
});

// ── Auth Notifier ─────────────────────────────────────────────────────────────

/// Kimlik doğrulama iş mantığını yöneten Riverpod StateNotifier.
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._repository, this._storage) : super(const AuthInitial());

  final AuthRepository _repository;
  final LocalStorageService _storage;

  // ── Init ──────────────────────────────────────────────────

  /// Splash ekranında çalışır; mevcut oturumu kontrol eder.
  Future<void> checkSession() async {
    state = const AuthLoading();
    try {
      await _storage.restoreAccessToken();

      final hasSession = await _storage.hasSession();
      if (!hasSession) {
        state = const AuthUnauthenticated();
        return;
      }

      final user = await _storage.getUser();
      if (user == null) {
        await _storage.clearAll();
        state = const AuthUnauthenticated();
        return;
      }

      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) {
        await _storage.clearAll();
        state = const AuthUnauthenticated();
        return;
      }

      try {
        final (newAccess, newRefresh) =
            await _repository.refreshToken(refreshToken);
        await _storage.setAccessToken(newAccess);
        await _storage.saveRefreshToken(newRefresh);
        state = AuthAuthenticated(user);
      } on AppException {
        // Access hâlâ varsa kısa süre idame etmeyi deneme — token invalid
        await _storage.clearAll();
        state = const AuthUnauthenticated();
      }
    } catch (_) {
      state = const AuthUnauthenticated();
    }
  }

  // ── Login ──────────────────────────────────────────────────

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = const AuthLoading();
    try {
      final (accessToken, refreshToken, user) = await _repository.login(
        email: email,
        password: password,
      );
      await _storage.setAccessToken(accessToken);
      await _storage.saveRefreshToken(refreshToken);
      await _storage.saveUser(user);
      state = AuthAuthenticated(user);
    } on AppException catch (e) {
      state = AuthError(e.message);
    } catch (_) {
      state = const AuthError('Beklenmeyen bir hata oluştu');
    }
  }

  // ── Register ───────────────────────────────────────────────

  Future<bool> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    state = const AuthLoading();
    try {
      await _repository.register(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
      );
      state = const AuthUnauthenticated();
      return true;
    } on AppException catch (e) {
      state = AuthError(e.message);
      return false;
    } catch (_) {
      state = const AuthError('Beklenmeyen bir hata oluştu');
      return false;
    }
  }

  // ── Logout ─────────────────────────────────────────────────

  Future<void> logout() async {
    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await _repository.logout(refreshToken);
      } catch (_) {
        // Sunucu hatası olsa bile lokal oturumu kapat
      }
    }
    await _storage.clearAll();
    state = const AuthUnauthenticated();
  }

  // ── Forgot Password ────────────────────────────────────────

  Future<ForgotPasswordResult?> forgotPassword(String email) async {
    state = const AuthLoading();
    try {
      final result = await _repository.forgotPassword(email);
      state = const AuthUnauthenticated();
      return result;
    } on AppException catch (e) {
      state = AuthError(e.message);
      return null;
    }
  }

  Future<bool> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    state = const AuthLoading();
    try {
      await _repository.resetPassword(token: token, newPassword: newPassword);
      state = const AuthUnauthenticated();
      return true;
    } on AppException catch (e) {
      state = AuthError(e.message);
      return false;
    }
  }

  /// Hata durumunu temizle.
  void clearError() {
    if (state is AuthError) {
      state = const AuthUnauthenticated();
    }
  }
}

// ── Provider ──────────────────────────────────────────────────────────────────

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authRepositoryProvider),
    ref.watch(localStorageServiceProvider),
  );
});
