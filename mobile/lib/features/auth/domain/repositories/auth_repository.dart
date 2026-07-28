import '../entities/auth_user.dart';

/// Auth repository contract (interface).
/// Data katmanı bu interface'i implemente eder.
abstract interface class AuthRepository {
  /// Kullanıcı girişi — token çifti döner.
  Future<(String accessToken, String refreshToken, AuthUser user)> login({
    required String email,
    required String password,
  });

  /// Yeni kullanıcı kaydı.
  Future<AuthUser> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'student',
  });

  /// Access token yenileme — yeni token çifti döner.
  Future<(String accessToken, String refreshToken)> refreshToken(
    String refreshToken,
  );

  /// Oturum kapatma — refresh token'ı iptal eder.
  Future<void> logout(String refreshToken);

  /// Şifre sıfırlama e-postası gönder.
  /// Dönüş: sunucu mesajı + isteğe bağlı geliştirme reset_url.
  Future<ForgotPasswordResult> forgotPassword(String email);

  /// Token ile yeni şifre belirle.
  Future<void> resetPassword({required String token, required String newPassword});
}

class ForgotPasswordResult {
  const ForgotPasswordResult({
    required this.message,
    this.emailSent = false,
    this.resetUrl,
    this.devResetToken,
  });

  final String message;
  final bool emailSent;
  final String? resetUrl;
  final String? devResetToken;
}

/// Result type alias for clarity
typedef AuthResult = (String accessToken, String refreshToken, AuthUser user);
typedef TokenPair = (String accessToken, String refreshToken);


