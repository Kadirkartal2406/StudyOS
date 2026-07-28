import '../../domain/entities/auth_user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/remote_auth_datasource.dart';

/// AuthRepository interface'inin gerçek implementasyonu.
/// Datasource'u çağırır ve domain entity'lerine dönüştürür.
class AuthRepositoryImpl implements AuthRepository {
  const AuthRepositoryImpl(this._datasource);

  final RemoteAuthDatasource _datasource;

  @override
  Future<(String, String, AuthUser)> login({
    required String email,
    required String password,
  }) async {
    final model = await _datasource.login(email: email, password: password);
    return (model.accessToken, model.refreshToken, model.user);
  }

  @override
  Future<AuthUser> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'student',
  }) async {
    final model = await _datasource.register(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
      role: role,
    );
    return model.user;
  }

  @override
  Future<(String, String)> refreshToken(String refreshToken) async {
    final model = await _datasource.refreshToken(refreshToken);
    return (model.accessToken, model.refreshToken);
  }

  @override
  Future<void> logout(String refreshToken) =>
      _datasource.logout(refreshToken);

  @override
  Future<ForgotPasswordResult> forgotPassword(String email) async {
    final data = await _datasource.forgotPassword(email);
    return ForgotPasswordResult(
      message: (data['message'] as String?) ??
          'E-posta kayıtlıysa sıfırlama bağlantısı gönderildi',
      emailSent: data['email_sent'] as bool? ?? false,
      resetUrl: data['reset_url'] as String?,
      devResetToken: data['dev_reset_token'] as String?,
    );
  }

  @override
  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) {
    return _datasource.resetPassword(token: token, newPassword: newPassword);
  }
}
