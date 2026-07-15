/// Kimlik doğrulama kullanıcı entity'si.
/// Domain katmanında saf Dart nesnesi — framework bağımlılığı yok.
class AuthUser {
  const AuthUser({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.role,
    this.isActive = true,
    this.isEmailVerified = false,
  });

  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String role; // 'student' | 'teacher' | 'institution_admin' | 'system_admin'
  final bool isActive;
  final bool isEmailVerified;

  String get fullName => '$firstName $lastName';

  bool get isStudent => role == 'student';

  factory AuthUser.fromJson(Map<String, dynamic> json) => AuthUser(
        id: json['id'] as String,
        email: json['email'] as String,
        firstName: json['first_name'] as String,
        lastName: json['last_name'] as String,
        role: json['role'] as String,
        isActive: json['is_active'] as bool? ?? true,
        isEmailVerified: json['is_email_verified'] as bool? ?? false,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'role': role,
        'is_active': isActive,
        'is_email_verified': isEmailVerified,
      };

  AuthUser copyWith({
    String? id,
    String? email,
    String? firstName,
    String? lastName,
    String? role,
    bool? isActive,
    bool? isEmailVerified,
  }) {
    return AuthUser(
      id: id ?? this.id,
      email: email ?? this.email,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      role: role ?? this.role,
      isActive: isActive ?? this.isActive,
      isEmailVerified: isEmailVerified ?? this.isEmailVerified,
    );
  }
}
