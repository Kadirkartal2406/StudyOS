import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/ai_settings_provider.dart';

/// AI Ayarları — Sprint-2.4 E2 (provider/model seçimi; API key yok).
class AiSettingsScreen extends ConsumerStatefulWidget {
  const AiSettingsScreen({super.key});

  @override
  ConsumerState<AiSettingsScreen> createState() => _AiSettingsScreenState();
}

class _AiSettingsScreenState extends ConsumerState<AiSettingsScreen> {
  final _modelCtrl = TextEditingController();
  bool _modelHydrated = false;

  @override
  void dispose() {
    _modelCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(aiSettingsProvider);
    if (state is AiSettingsLoaded && !_modelHydrated) {
      final raw =
          state.settings.preferredModel ?? state.settings.effectiveModel ?? '';
      final lowered = raw.trim().toLowerCase();
      _modelCtrl.text =
          (lowered.isEmpty ||
                  lowered == 'template' ||
                  lowered == 'null' ||
                  lowered == 'none')
              ? ''
              : raw;
      _modelHydrated = true;
    }

    return Scaffold(
      appBar: AppBar(title: const Text('AI Ayarları')),
      body: switch (state) {
        AiSettingsLoading() => const Center(child: CircularProgressIndicator()),
        AiSettingsError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.read(aiSettingsProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        AiSettingsLoaded(:final settings, :final errorMessage) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (errorMessage != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Text(
                    errorMessage,
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  ),
                ),
              Text(
                'Aktif sağlayıcı',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              ...settings.availableProviders.map(
                (p) => RadioListTile<String>(
                  title: Text(p),
                  value: p,
                  groupValue:
                      settings.preferredProvider ?? settings.effectiveProvider,
                  onChanged: (v) {
                    if (v != null) {
                      ref.read(aiSettingsProvider.notifier).setProvider(v);
                    }
                  },
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _modelCtrl,
                decoration: const InputDecoration(
                  labelText: 'Model (opsiyonel)',
                  border: OutlineInputBorder(),
                  helperText: 'Boş bırakılırsa sunucu varsayılanı kullanılır',
                ),
              ),
              const SizedBox(height: 8),
              FilledButton(
                onPressed: () => ref
                    .read(aiSettingsProvider.notifier)
                    .setModel(_modelCtrl.text),
                child: const Text('Modeli kaydet'),
              ),
              const SizedBox(height: 24),
              Text('Debug', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              _DebugRow(
                label: 'Effective provider',
                value: settings.effectiveProvider,
              ),
              _DebugRow(
                label: 'Effective model',
                value: settings.effectiveModel ?? '-',
              ),
              _DebugRow(label: 'Fallback', value: settings.fallbackProvider),
              _DebugRow(
                label: 'Streaming',
                value: settings.streamingEnabled ? 'açık' : 'kapalı (stub)',
              ),
              if (settings.debug.isNotEmpty) ...[
                const SizedBox(height: 8),
                ...settings.debug.entries.map(
                  (e) => _DebugRow(label: e.key, value: '${e.value}'),
                ),
              ],
              const SizedBox(height: 16),
              Text(
                'API anahtarları yalnızca sunucu .env üzerinden yönetilir; '
                'bu ekranda key girilmez.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
      },
    );
  }
}

class _DebugRow extends StatelessWidget {
  const _DebugRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Expanded(child: Text(label)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
