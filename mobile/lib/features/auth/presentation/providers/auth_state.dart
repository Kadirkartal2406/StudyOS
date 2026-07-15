import '../../domain/entities/auth_user.dart';

/// Auth feature için mühürlü (sealed) durum sınıfı.
/// Dart 3 sealed class — exhaustive switch garantisi.
sealed class AuthState {
  const AuthState();
}

/// İlk yüklenme — token kontrolü henüz yapılmadı.
class AuthInitial extends AuthState {
  const AuthInitial();
}

/// Token kontrolü / giriş / kayıt işlemi devam ediyor.
class AuthLoading extends AuthState {
  const AuthLoading();
}

/// Kullanıcı giriş yapmış.
class AuthAuthenticated extends AuthState {
  const AuthAuthenticated(this.user);

  final AuthUser user;
}

/// Kullanıcı giriş yapmamış veya oturumu sonlanmış.
class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
}

/// Giriş / kayıt işleminde hata oluştu.
class AuthError extends AuthState {
  const AuthError(this.message);

  final String message;
}
