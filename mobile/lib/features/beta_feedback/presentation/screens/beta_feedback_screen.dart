import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/analytics/analytics_service.dart';
import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/constants/app_config.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_spacing.dart';

/// Sprint 21 RC.9 — Beta Feedback (feature freeze istisnası: beta altyapısı).
class BetaFeedbackScreen extends ConsumerStatefulWidget {
  const BetaFeedbackScreen({super.key});

  @override
  ConsumerState<BetaFeedbackScreen> createState() => _BetaFeedbackScreenState();
}

class _BetaFeedbackScreenState extends ConsumerState<BetaFeedbackScreen> {
  String _kind = 'bug';
  final _message = TextEditingController();
  final _screen = TextEditingController();
  bool _sending = false;
  String? _error;

  @override
  void dispose() {
    _message.dispose();
    _screen.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final text = _message.text.trim();
    if (text.length < 5) {
      setState(() => _error = 'Lütfen en az 5 karakter yaz.');
      return;
    }
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      final dio = ref.read(dioClientProvider);
      await dio.post(
        ApiEndpoints.betaFeedback,
        data: {
          'kind': _kind,
          'message': text,
          'screen_hint': _screen.text.trim().isEmpty ? null : _screen.text.trim(),
          'app_version': AppConfig.appVersion,
          'platform': defaultTargetPlatform.name,
        },
      );
      ref.read(analyticsServiceProvider).trackSync(AnalyticsEvents.feedbackSent);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Teşekkürler — geri bildiriminiz alındı')),
      );
      context.pop();
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _sending = false;
        _error = 'Gönderilemedi. Bağlantını kontrol et.';
      });
      return;
    }
    if (mounted) setState(() => _sending = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Geri bildirim')),
      body: ListView(
        padding: AppSpacing.pageWide,
        children: [
          Text(
            'Kapalı beta — sorun veya önerini paylaş.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: AppSpacing.lg),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'bug', label: Text('Sorun')),
              ButtonSegment(value: 'suggestion', label: Text('Öneri')),
              ButtonSegment(value: 'other', label: Text('Diğer')),
            ],
            selected: {_kind},
            onSelectionChanged: (s) => setState(() => _kind = s.first),
          ),
          const SizedBox(height: AppSpacing.md),
          TextField(
            controller: _screen,
            decoration: const InputDecoration(
              labelText: 'Ekran (opsiyonel)',
              hintText: 'ör. Today, Assessment',
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          TextField(
            controller: _message,
            minLines: 5,
            maxLines: 10,
            decoration: const InputDecoration(
              labelText: 'Mesaj',
              alignLabelWithHint: true,
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
          const SizedBox(height: AppSpacing.lg),
          FilledButton(
            onPressed: _sending ? null : _submit,
            child: _sending
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Gönder'),
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Sürüm ${AppConfig.appVersion}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
