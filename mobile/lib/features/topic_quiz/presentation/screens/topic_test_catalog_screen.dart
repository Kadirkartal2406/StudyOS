import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/widgets/app_error_view.dart';
import '../../../../shared/widgets/ds.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../data/topic_test_remote_datasource.dart';

/// Published weekly topic tests — no Gemini on start.
class TopicTestCatalogScreen extends ConsumerStatefulWidget {
  const TopicTestCatalogScreen({
    super.key,
    required this.subjectCode,
    required this.topicCode,
    this.topicName,
    this.exam,
  });

  final String subjectCode;
  final String topicCode;
  final String? topicName;
  final String? exam;

  @override
  ConsumerState<TopicTestCatalogScreen> createState() =>
      _TopicTestCatalogScreenState();
}

class _TopicTestCatalogScreenState
    extends ConsumerState<TopicTestCatalogScreen> {
  bool _loading = true;
  String? _error;
  TopicTestCatalog? _catalog;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  String get _exam {
    final fromQuery = widget.exam?.trim();
    if (fromQuery != null && fromQuery.isNotEmpty) return fromQuery;
    final profile = ref.read(learningProfileProvider).valueOrNull;
    return (profile?.activeExamType ?? 'kpss').trim().toLowerCase();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final catalog = await ref.read(topicTestDatasourceProvider).listCatalog(
            exam: _exam,
            subjectCode: widget.subjectCode,
            topicCode: widget.topicCode,
          );
      if (!mounted) return;
      setState(() {
        _catalog = catalog;
        _loading = false;
      });
    } on AppException catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.message;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Testler yüklenemedi.';
        _loading = false;
      });
    }
  }

  Color _diffColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return const Color(0xFF2E7D32);
      case 'hard':
        return const Color(0xFFC62828);
      default:
        return const Color(0xFFF9A825);
    }
  }

  String _statusLabel(TopicTestListItem t) {
    if (t.userStatus == 'submitted') {
      if (t.accuracyPct != null) {
        return '%${t.accuracyPct!.round()}';
      }
      return 'Tamamlandı';
    }
    if (t.userStatus == 'in_progress') return 'Devam';
    return 'Başla';
  }

  @override
  Widget build(BuildContext context) {
    final title = widget.topicName ??
        _catalog?.topicName ??
        widget.topicCode;

    return Scaffold(
      appBar: AppBar(
        title: Text('Konu Testleri'),
        actions: [
          IconButton(
            tooltip: 'Yenile',
            onPressed: _load,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? AppErrorView(message: _error!, onRetry: _load)
              : _buildBody(context, title),
    );
  }

  Widget _buildBody(BuildContext context, String title) {
    final catalog = _catalog;
    if (catalog == null || catalog.tests.isEmpty) {
      return EmptyState(
        icon: Icons.hourglass_top_outlined,
        title: 'Bu konu için yeni testler hazırlanıyor.',
        message:
            'Hazır testler yayınlandığında burada görünecek. '
            'AI ile anlık üretim için Menü → Soru Üret.',
        ctaLabel: 'Yenile',
        onCta: _load,
      );
    }

    final byWeek = <String, List<TopicTestListItem>>{};
    for (final t in catalog.tests) {
      byWeek.putIfAbsent(t.weekId, () => []).add(t);
    }
    final weeks = byWeek.keys.toList()
      ..sort((a, b) => b.compareTo(a));

    return ListView(
      padding: AppSpacing.pageWide,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          'Her test 10 soru · Gemini beklemeden çöz',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: AppSpacing.lg),
        for (final week in weeks) ...[
          Text(
            week,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: AppSpacing.sm),
          ...byWeek[week]!.map((t) {
            final color = _diffColor(t.difficulty);
            return Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.sm),
              child: MetricTile(
                title: t.title,
                subtitle:
                    '${t.questionCount} soru · ${_statusLabel(t)}',
                leading: Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                onTap: () {
                  context.push(
                    '/topic-test-session'
                    '?test_id=${t.id}'
                    '&subject_code=${Uri.encodeComponent(widget.subjectCode)}'
                    '&topic_code=${Uri.encodeComponent(widget.topicCode)}'
                    '&topic_name=${Uri.encodeComponent(title)}',
                  );
                },
              ),
            );
          }),
          const SizedBox(height: AppSpacing.md),
        ],
      ],
    );
  }
}
