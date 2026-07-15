import '../../domain/entities/auth_user.dart';

/// API'den gelen login/register yanıtını parse eden model.
/// Data katmanında kalır; domain katmanına AuthUser entity olarak iletilir.
class AuthResponseModel {
  const AuthResponseModel({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });

  final String accessToken;
  final String refreshToken;
  final AuthUser user;

  factory AuthResponseModel.fromJson(Map<String, dynamic> json) {
    return AuthResponseModel(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}

/// Token yenileme yanıtı modeli.
class TokenRefreshModel {
  const TokenRefreshModel({
    required this.accessToken,
    required this.refreshToken,
  });

  final String accessToken;
  final String refreshToken;

  factory TokenRefreshModel.fromJson(Map<String, dynamic> json) {
    return TokenRefreshModel(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
    );
  }
}
