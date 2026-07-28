import '../../domain/entities/dashboard_entity.dart';

/// Sprint-3.1.B — Active Exam'e göre Hero/layout vurgusu (if-else kaosu yok).
abstract class DashboardLayoutStrategy {
  String formatPrimaryTarget(DashboardExamTargetEntity? target);

  List<String> focusLabels();
}

DashboardLayoutStrategy dashboardLayoutFor(String? activeExamType) {
  final key = (activeExamType ?? '').toLowerCase();
  return switch (key) {
    'yks' || 'tyt' || 'ayt' => const YksDashboardLayout(),
    'kpss' => const KpssDashboardLayout(),
    'yds' => const YdsDashboardLayout(),
    _ => const DefaultDashboardLayout(),
  };
}

class YksDashboardLayout implements DashboardLayoutStrategy {
  const YksDashboardLayout();

  @override
  String formatPrimaryTarget(DashboardExamTargetEntity? target) {
    if (target == null) return 'YKS hedefi';
    final uni = target.targetUniversity?.trim();
    final dept = target.targetDepartment?.trim();
    if (uni != null && uni.isNotEmpty) {
      if (dept != null && dept.isNotEmpty) return '$uni $dept';
      return uni;
    }
    if (target.targetNet != null) {
      return 'Hedef net ${target.targetNet!.toStringAsFixed(0)}';
    }
    return target.examType.toUpperCase();
  }

  @override
  List<String> focusLabels() => const ['Net', 'Üniversite', 'Bölüm'];
}

class KpssDashboardLayout implements DashboardLayoutStrategy {
  const KpssDashboardLayout();

  static const _branchLabels = {
    'lisans': 'Lisans',
    'onlisans': 'Önlisans',
    'ortaogretim': 'Ortaöğretim',
  };

  @override
  String formatPrimaryTarget(DashboardExamTargetEntity? target) {
    if (target == null) return 'KPSS hedefi';
    final branch = target.branch?.trim().toLowerCase();
    if (branch != null && branch.isNotEmpty) {
      return 'KPSS ${_branchLabels[branch] ?? branch}';
    }
    if (target.targetScore != null) {
      return 'KPSS ${target.targetScore!.toStringAsFixed(0)}';
    }
    return 'KPSS';
  }

  @override
  List<String> focusLabels() =>
      const ['Türkçe', 'Matematik', 'Tarih', 'Coğrafya', 'Vatandaşlık'];
}

class YdsDashboardLayout implements DashboardLayoutStrategy {
  const YdsDashboardLayout();

  @override
  String formatPrimaryTarget(DashboardExamTargetEntity? target) {
    if (target == null) return 'YDS hedefi';
    if (target.targetScore != null) {
      return 'YDS ${target.targetScore!.toStringAsFixed(0)}';
    }
    return 'YDS';
  }

  @override
  List<String> focusLabels() => const [
        'Vocabulary',
        'Grammar',
        'Reading',
        'Translation',
        'Puan',
      ];
}

class DefaultDashboardLayout implements DashboardLayoutStrategy {
  const DefaultDashboardLayout();

  @override
  String formatPrimaryTarget(DashboardExamTargetEntity? target) {
    if (target == null) return 'Hedef belirle';
    final type = target.examType.toUpperCase();
    if (target.targetScore != null) {
      return '$type ${target.targetScore!.toStringAsFixed(0)}';
    }
    if (target.targetNet != null) {
      return '$type net ${target.targetNet!.toStringAsFixed(0)}';
    }
    final uni = target.targetUniversity?.trim();
    if (uni != null && uni.isNotEmpty) return uni;
    return type;
  }

  @override
  List<String> focusLabels() => const ['Hedef', 'İlerleme', 'Plan'];
}
