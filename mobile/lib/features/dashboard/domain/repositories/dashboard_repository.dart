import '../entities/dashboard_entity.dart';

/// Dashboard repository contract (interface).
/// Data katmanı bu interface'i implemente eder.
abstract interface class DashboardRepository {
  /// Giriş yapan kullanıcı için ana ekran özet verisini getirir.
  Future<DashboardEntity> getDashboard();
}
