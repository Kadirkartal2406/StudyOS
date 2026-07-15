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
  Future<void> forgotPassword(String email) =>
      _datasource.forgotPassword(email);
}
