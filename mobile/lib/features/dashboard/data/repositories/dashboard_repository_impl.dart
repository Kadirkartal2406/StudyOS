import '../../domain/entities/dashboard_entity.dart';
import '../../domain/repositories/dashboard_repository.dart';
import '../datasources/dashboard_remote_datasource.dart';

/// DashboardRepository interface'inin gerçek implementasyonu.
/// Datasource'u çağırır ve domain entity'sine dönüştürür.
class DashboardRepositoryImpl implements DashboardRepository {
  const DashboardRepositoryImpl(this._datasource);

  final DashboardRemoteDatasource _datasource;

  @override
  Future<DashboardEntity> getDashboard() async {
    final model = await _datasource.getDashboard();
    return model.toEntity();
  }
}
