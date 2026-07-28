import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/analytics/analytics_service.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/platform_providers.dart';
import '../../../../core/platform/widget_service.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../auth/presentation/providers/auth_state.dart';
import '../../../notification_settings/presentation/providers/notification_settings_provider.dart';
import '../../data/datasources/dashboard_remote_datasource.dart';
import '../../data/repositories/dashboard_repository_impl.dart';
import '../../domain/entities/dashboard_entity.dart';
import '../../domain/repositories/dashboard_repository.dart';
import 'dashboard_state.dart';

// ── Dependency Injection ──────────────────────────────────────────────────────

final _remoteDatasourceProvider = Provider<DashboardRemoteDatasource>((ref) {
  return DashboardRemoteDatasource(ref.watch(dioClientProvider));
});

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepositoryImpl(ref.watch(_remoteDatasourceProvider));
});

// ── Dashboard Notifier ─────────────────────────────────────────────────────────

/// Dashboard verisinin yüklenmesini yöneten Riverpod StateNotifier.
class DashboardNotifier extends StateNotifier<DashboardState> {
  DashboardNotifier(
    this._repository,
    this._widgetService, {
    AnalyticsService? analytics,
    bool Function()? shouldAutoUpdateWidget,
    bool autoLoad = true,
  })  : _analytics = analytics,
        _shouldAutoUpdateWidget = shouldAutoUpdateWidget ?? (() => true),
        super(const DashboardInitial()) {
    if (autoLoad) {
      load();
    }
  }

  final DashboardRepository _repository;
  final WidgetService _widgetService;
  final AnalyticsService? _analytics;
  final bool Function() _shouldAutoUpdateWidget;

  /// Dashboard verisini backend'den yükler.
  Future<void> load() async {
    state = const DashboardLoading();
    try {
      final dashboard = await _repository.getDashboard();
      state = DashboardLoaded(dashboard);
      _analytics?.trackSync(AnalyticsEvents.todayViewed);
      if (dashboard.coachToday != null) {
        _analytics?.trackSync(AnalyticsEvents.coachViewed);
      }
      await _syncWidget(dashboard);
    } on AppException catch (e) {
      state = DashboardError(e.message);
    } catch (_) {
      state = const DashboardError('Beklenmeyen bir hata oluştu');
    }
  }

  Future<void> _syncWidget(DashboardEntity dashboard) async {
    if (!_shouldAutoUpdateWidget()) return;
    try {
      String? goalLabel;
      final weekly = dashboard.weeklyGoals;
      if (weekly.isNotEmpty) {
        final sorted = [...weekly]
          ..sort((a, b) => b.progress.compareTo(a.progress));
        goalLabel =
            'Hedef: ${sorted.first.progress.toStringAsFixed(0)}%';
      }
      await _widgetService.updateFromCache(
        WidgetSnapshot(
          todayStudyMinutes: dashboard.todayStudyMinutes,
          dailyGoalMinutes: dashboard.dailyStudyGoalMinutes,
          progressPercentage: dashboard.dailyProgressPercentage,
          activePlanTitle: dashboard.todayStudiedTopic,
          goalLabel: goalLabel,
        ),
      );
    } catch (_) {
      // Widget güncellemesi UI'yi bozmamalı.
    }
  }

  /// Retry butonu — veriyi yeniden yükler.
  Future<void> retry() => load();
}

// ── Provider ──────────────────────────────────────────────────────────────────

final dashboardProvider =
    StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  // Hesap değişince (logout/login/register) notifier yeniden kurulur —
  // aksi halde eski kullanıcının "Şimdi yap" kartı yeni hesapta kalır.
  final auth = ref.watch(authProvider);
  final userId = switch (auth) {
    AuthAuthenticated(:final user) => user.id,
    _ => null,
  };

  return DashboardNotifier(
    ref.watch(dashboardRepositoryProvider),
    ref.watch(widgetServiceProvider),
    analytics: ref.watch(analyticsServiceProvider),
    autoLoad: userId != null,
    shouldAutoUpdateWidget: () {
      final settings = ref.read(notificationSettingsProvider);
      if (settings is NotificationSettingsLoaded) {
        return settings.settings.widgetAutoUpdateEnabled;
      }
      return true;
    },
  );
});
