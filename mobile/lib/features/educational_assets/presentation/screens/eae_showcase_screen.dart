library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/asset_contracts/asset_manifest_contract.dart';
import '../../../../core/asset_engine/asset_bundle_decoder.dart';
import '../../../../core/asset_engine/providers/eae_render_provider.dart';
import '../../../../shared/widgets/eae_vector_canvas_widget.dart';
import '../../data/models/asset_search_query_dto.dart';
import '../providers/asset_search_provider.dart';

/// Demo / QA surface for Turkey admin geography EAE package.
class EAEShowcaseScreen extends ConsumerStatefulWidget {
  const EAEShowcaseScreen({super.key});

  @override
  ConsumerState<EAEShowcaseScreen> createState() => _EAEShowcaseScreenState();
}

class _EAEShowcaseScreenState extends ConsumerState<EAEShowcaseScreen> {
  static const _turkeyAdminUri = 'studyos://assets/geography/turkey_admin/v1';

  EAEAssetManifestContract? _manifest;
  String? _svgContent;
  Object? _loadError;
  bool _loading = true;
  EAENodeContract? _selectedNode;
  bool _enableMultiSelect = false;
  String _sourceLabel = '';

  @override
  void initState() {
    super.initState();
    // API gelmeden önce yerel demo göster — boş ekran / redirect hissi olmasın.
    _loadDemoFallback();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadTurkeyAdmin());
  }

  Future<void> _loadTurkeyAdmin() async {
    try {
      final repo = ref.read(assetRepositoryProvider);
      // Prefer logical URI (API resolves UUID or URI).
      try {
        final bytes = await repo.downloadBundle(_turkeyAdminUri);
        final decoded = EAEAssetBundleDecoder.decodeBundleBytes(bytes);
        if (!mounted) return;
        setState(() {
          _manifest = decoded.manifest;
          _svgContent = decoded.svgContent;
          _sourceLabel = 'registry bundle · $_turkeyAdminUri';
          _loading = false;
          _loadError = null;
        });
        return;
      } catch (_) {
        // Fall through to search / keep local demo.
      }

      final results = await repo.searchAssets(
        const AssetSearchQueryDTO(
          query: 'turkey_admin',
          domain: 'geography',
          pageSize: 5,
        ),
      );
      if (results.isNotEmpty) {
        final hit = results.first;
        final key = hit.assetId;
        try {
          final bytes = await repo.downloadBundle(key);
          final decoded = EAEAssetBundleDecoder.decodeBundleBytes(bytes);
          if (!mounted) return;
          setState(() {
            _manifest = decoded.manifest;
            _svgContent = decoded.svgContent;
            _sourceLabel = 'search · ${hit.assetId}';
            _loading = false;
            _loadError = null;
          });
          return;
        } catch (_) {
          /* keep demo */
        }
      }
      if (!mounted) return;
      setState(() {
        _loading = false;
        if (_sourceLabel.isEmpty || !_sourceLabel.contains('demo')) {
          _sourceLabel = 'yerel demo (registry yok)';
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _loadError = e;
        _sourceLabel = 'yerel demo (hata: $e)';
      });
    }
  }

  void _loadDemoFallback({Object? error}) {
    final demo = EAEAssetManifestContract.fromJson({
      'schema_version': '1.0',
      'asset_id': _turkeyAdminUri,
      'version': '1.0.0',
      'domain': 'geography',
      'format': 'svg',
      'title': {
        'tr': 'Türkiye İdari Haritası (yerel demo)',
        'en': 'Turkey Admin (local demo)',
      },
      'viewport': {
        'width': 800.0,
        'height': 450.0,
        'default_scale': 1.0,
        'max_scale': 8.0,
      },
      'layers': [
        {
          'id': 'provinces_layer',
          'z_index': 1,
          'min_lod': 1.0,
          'nodes': [
            {
              'id': 'turkey_admin_v1::province::konya',
              'name': {'tr': 'Konya', 'en': 'Konya'},
              'bounding_box': [100.0, 150.0, 300.0, 350.0],
              'attributes': {
                'region': 'İç Anadolu Bölgesi',
                'pedagogical_note':
                    'Türkiye\'nin yüzölçümü bakımından en büyük ili.',
              },
            },
            {
              'id': 'turkey_admin_v1::province::ankara',
              'name': {'tr': 'Ankara', 'en': 'Ankara'},
              'bounding_box': [320.0, 80.0, 480.0, 220.0],
              'attributes': {
                'region': 'İç Anadolu Bölgesi',
                'pedagogical_note': 'Türkiye Cumhuriyeti\'nin başkenti.',
              },
            },
            {
              'id': 'turkey_admin_v1::province::izmir',
              'name': {'tr': 'İzmir', 'en': 'Izmir'},
              'bounding_box': [500.0, 180.0, 680.0, 340.0],
              'attributes': {
                'region': 'Ege Bölgesi',
                'pedagogical_note':
                    'Ege bölgesinin en büyük sanayi ve liman kenti.',
              },
            },
          ],
        },
      ],
      'tags': ['cografya', 'turkiye', 'harita', 'eae_demo'],
    });

    _manifest = demo;
    _svgContent = '''
<svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">
  <g id="provinces">
    <path id="turkey_admin_v1::province::konya" d="M 100 150 L 300 150 L 300 350 L 100 350 Z"/>
    <path id="turkey_admin_v1::province::ankara" d="M 320 80 L 480 80 L 480 220 L 320 220 Z"/>
    <path id="turkey_admin_v1::province::izmir" d="M 500 180 L 680 180 L 680 340 L 500 340 Z"/>
  </g>
</svg>
''';
    _sourceLabel = error != null
        ? 'yerel demo (registry: $error)'
        : 'yerel demo';
    _loadError = error;
    _loading = false;
  }

  @override
  Widget build(BuildContext context) {
    final renderState = ref.watch(eaeRenderNotifierProvider);
    final theme = Theme.of(context);
    final manifest = _manifest;
    final svg = _svgContent;

    return Scaffold(
      appBar: AppBar(
        title: const Text('StudyOS EAE — Türkiye İdari'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Yeniden yükle',
            onPressed: _loading ? null : _loadTurkeyAdmin,
          ),
          IconButton(
            icon: Icon(
              _enableMultiSelect ? Icons.checklist_rtl : Icons.touch_app,
              color: _enableMultiSelect ? theme.colorScheme.primary : null,
            ),
            tooltip: 'Çoklu Seçim',
            onPressed: () {
              setState(() => _enableMultiSelect = !_enableMultiSelect);
            },
          ),
          IconButton(
            icon: const Icon(Icons.clear_all),
            tooltip: 'Seçimi Temizle',
            onPressed: () {
              ref.read(eaeRenderNotifierProvider.notifier).clearSelection();
              setState(() => _selectedNode = null);
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  color: theme.colorScheme.primaryContainer
                      .withValues(alpha: 0.3),
                  child: Text(
                    'Kaynak: $_sourceLabel',
                    style: theme.textTheme.bodySmall,
                  ),
                ),
                Expanded(
                  child: manifest == null || svg == null
                      ? Center(
                          child: Text('Asset yok: ${_loadError ?? "bilinmiyor"}'),
                        )
                      : Center(
                          child: AspectRatio(
                            aspectRatio: manifest.viewport.width /
                                (manifest.viewport.height > 0
                                    ? manifest.viewport.height
                                    : 450),
                            child: Card(
                              elevation: 4,
                              margin: const EdgeInsets.all(16),
                              clipBehavior: Clip.antiAlias,
                              child: EAEVectorCanvasWidget(
                                manifest: manifest,
                                svgContent: svg,
                                enableMultiSelect: _enableMultiSelect,
                                onNodeTapped: (node) {
                                  setState(() => _selectedNode = node);
                                },
                              ),
                            ),
                          ),
                        ),
                ),
                if (_selectedNode != null)
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(20),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.location_on,
                                color: theme.colorScheme.primary),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _selectedNode!.getLocalizedName('tr'),
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            Chip(
                              label: Text(
                                'LOD ${renderState.currentScale.toStringAsFixed(1)}x',
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'EAE Node ID: ${_selectedNode!.id}',
                          style: theme.textTheme.bodySmall?.copyWith(
                            fontFamily: 'monospace',
                          ),
                        ),
                        if (_selectedNode!.attributes['pedagogical_note'] !=
                            null) ...[
                          const SizedBox(height: 8),
                          Text(
                            '${_selectedNode!.attributes['pedagogical_note']}',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontStyle: FontStyle.italic,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
              ],
            ),
    );
  }
}
