import 'package:flutter_test/flutter_test.dart';
import 'package:studyos_mobile/features/dashboard/domain/entities/dashboard_entity.dart';
import 'package:studyos_mobile/features/dashboard/presentation/widgets/dashboard_layout_strategy.dart';

void main() {
  test('YKS layout formats university + department', () {
    final line = const YksDashboardLayout().formatPrimaryTarget(
      const DashboardExamTargetEntity(
        examType: 'yks',
        targetUniversity: 'ODTÜ',
        targetDepartment: 'Bilgisayar',
      ),
    );
    expect(line, 'ODTÜ Bilgisayar');
  });

  test('KPSS layout formats branch', () {
    final line = const KpssDashboardLayout().formatPrimaryTarget(
      const DashboardExamTargetEntity(
        examType: 'kpss',
        branch: 'lisans',
      ),
    );
    expect(line, 'KPSS Lisans');
  });

  test('YDS layout formats score', () {
    final line = const YdsDashboardLayout().formatPrimaryTarget(
      const DashboardExamTargetEntity(
        examType: 'yds',
        targetScore: 85,
      ),
    );
    expect(line, 'YDS 85');
  });

  test('dashboardLayoutFor selects strategy by active exam', () {
    expect(dashboardLayoutFor('yks'), isA<YksDashboardLayout>());
    expect(dashboardLayoutFor('kpss'), isA<KpssDashboardLayout>());
    expect(dashboardLayoutFor('yds'), isA<YdsDashboardLayout>());
    expect(dashboardLayoutFor('ales'), isA<DefaultDashboardLayout>());
  });
}
