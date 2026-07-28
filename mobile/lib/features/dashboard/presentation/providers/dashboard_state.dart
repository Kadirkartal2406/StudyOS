import '../../domain/entities/dashboard_entity.dart';

/// Dashboard feature için mühürlü (sealed) durum sınıfı.
/// Dart 3 sealed class — exhaustive switch garantisi.
sealed class DashboardState {
  const DashboardState();
}

/// İlk yüklenme — henüz istek atılmadı.
class DashboardInitial extends DashboardState {
  const DashboardInitial();
}

/// `/dashboard` isteği devam ediyor.
class DashboardLoading extends DashboardState {
  const DashboardLoading();
}

/// Dashboard verisi başarıyla yüklendi.
class DashboardLoaded extends DashboardState {
  const DashboardLoaded(this.dashboard);

  final DashboardEntity dashboard;
}

/// Dashboard verisi yüklenirken hata oluştu.
class DashboardError extends DashboardState {
  const DashboardError(this.message);

  final String message;
}
