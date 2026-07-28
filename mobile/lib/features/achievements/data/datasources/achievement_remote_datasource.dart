import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/achievement_entity.dart';

class AchievementRemoteDatasource {
  const AchievementRemoteDatasource(this._dio);

  final Dio _dio;

  Future<List<AchievementEntity>> listCatalog() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.achievements,
      );
      final data = _extract(response.data) as List<dynamic>? ?? [];
      return data
          .map((e) => _fromCatalog(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<AchievementEntity>> listUnlocked() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.achievementsUnlocked,
      );
      final data = _extract(response.data) as List<dynamic>? ?? [];
      return data.map((e) {
        final m = e as Map<String, dynamic>;
        final ach = m['achievement'] as Map<String, dynamic>? ?? {};
        return AchievementEntity(
          id: ach['id'] as String? ?? m['achievement_id'] as String,
          code: ach['code'] as String? ?? '',
          title: ach['title'] as String? ?? '',
          description: ach['description'] as String? ?? '',
          category: ach['category'] as String? ?? '',
          tier: ach['tier'] as String? ?? 'easy',
          points: ach['points'] as int? ?? 0,
          iconKey: ach['icon_key'] as String? ?? 'trophy',
          reason: m['reason'] as String?,
          unlockedAt: m['unlocked_at'] == null
              ? null
              : DateTime.parse(m['unlocked_at'] as String),
          unlocked: true,
        );
      }).toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<AchievementEntity>> listProgress() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.achievementsProgress,
      );
      final data = _extract(response.data) as List<dynamic>? ?? [];
      return data.map((e) {
        final m = e as Map<String, dynamic>;
        final ach = m['achievement'] as Map<String, dynamic>? ?? {};
        return AchievementEntity(
          id: ach['id'] as String? ?? m['achievement_id'] as String,
          code: ach['code'] as String? ?? '',
          title: ach['title'] as String? ?? '',
          description: ach['description'] as String? ?? '',
          category: ach['category'] as String? ?? '',
          tier: ach['tier'] as String? ?? 'easy',
          points: ach['points'] as int? ?? 0,
          iconKey: ach['icon_key'] as String? ?? 'trophy',
          unlocked: m['unlocked'] as bool? ?? false,
          currentValue: (m['current_value'] as num?)?.toDouble() ?? 0,
          targetValue: (m['target_value'] as num?)?.toDouble() ?? 1,
        );
      }).toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<AchievementEntity>> check({String? event}) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.achievementsCheck,
        data: {'event': event},
      );
      final data = _extract(response.data) as Map<String, dynamic>;
      final newly = data['newly_unlocked'] as List<dynamic>? ?? [];
      return newly.map((e) {
        final m = e as Map<String, dynamic>;
        final ach = m['achievement'] as Map<String, dynamic>? ?? {};
        return AchievementEntity(
          id: ach['id'] as String? ?? m['achievement_id'] as String,
          code: ach['code'] as String? ?? '',
          title: ach['title'] as String? ?? '',
          description: ach['description'] as String? ?? '',
          category: ach['category'] as String? ?? '',
          tier: ach['tier'] as String? ?? 'easy',
          points: ach['points'] as int? ?? 0,
          iconKey: ach['icon_key'] as String? ?? 'trophy',
          reason: m['reason'] as String?,
          unlocked: true,
        );
      }).toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AchievementExplainEntity> explain(String id) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.achievementExplain(id),
      );
      final json = _extract(response.data) as Map<String, dynamic>;
      return AchievementExplainEntity(
        achievementId: json['achievement_id'] as String,
        explanation: json['explanation'] as String? ?? '',
        provider: json['provider'] as String? ?? 'null',
        reason: json['reason'] as String? ?? '',
        code: json['code'] as String? ?? '',
        title: json['title'] as String? ?? '',
        usedFallback: json['used_fallback'] as bool? ?? false,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  AchievementEntity _fromCatalog(Map<String, dynamic> json) {
    return AchievementEntity(
      id: json['id'] as String,
      code: json['code'] as String? ?? '',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      category: json['category'] as String? ?? '',
      tier: json['tier'] as String? ?? 'easy',
      points: json['points'] as int? ?? 0,
      iconKey: json['icon_key'] as String? ?? 'trophy',
    );
  }

  dynamic _extract(Map<String, dynamic>? body) => body?['data'];
}
