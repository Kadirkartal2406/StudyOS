import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/asset_contracts/asset_manifest_contract.dart';
import '../../../../core/asset_engine/asset_bundle_decoder.dart';
import '../../../../core/asset_engine/providers/eae_render_provider.dart';
import '../../../../shared/widgets/eae_vector_canvas_widget.dart';
import '../../data/models/asset_search_query_dto.dart';
import '../providers/asset_search_provider.dart';

class MapViewerScreen extends ConsumerStatefulWidget {
  final String uri;
  final String title;

  const MapViewerScreen({
    super.key,
    required this.uri,
    required this.title,
  });

  @override
  ConsumerState<MapViewerScreen> createState() => _MapViewerScreenState();
}

class _MapViewerScreenState extends ConsumerState<MapViewerScreen> {
  EAEAssetManifestContract? _manifest;
  String? _svgContent;
  Object? _loadError;
  bool _loading = true;
  bool _enableMultiSelect = false;
  bool _isLandscape = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadAsset());
  }

  @override
  void dispose() {
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
    super.dispose();
  }

  Future<void> _loadAsset() async {
    try {
      final repo = ref.read(assetRepositoryProvider);
      try {
        final bytes = await repo.downloadBundle(widget.uri);
        final decoded = EAEAssetBundleDecoder.decodeBundleBytes(bytes);
        if (!mounted) return;
        setState(() {
          _manifest = decoded.manifest;
          _svgContent = decoded.svgContent;
          _loading = false;
          _loadError = null;
        });
        return;
      } catch (_) {
        // Fall through to search.
      }

      final results = await repo.searchAssets(
        AssetSearchQueryDTO(
          query: widget.uri.split('/').lastWhere((e) => e != 'v1', orElse: () => 'turkey_admin'),
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
            _loading = false;
            _loadError = null;
          });
          return;
        } catch (_) {}
      }

      if (!mounted) return;
      setState(() {
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _loadError = e;
      });
    }
  }

  void _toggleRotation() {
    setState(() {
      _isLandscape = !_isLandscape;
    });
    if (_isLandscape) {
      SystemChrome.setPreferredOrientations([
        DeviceOrientation.landscapeLeft,
        DeviceOrientation.landscapeRight,
      ]);
    } else {
      SystemChrome.setPreferredOrientations([
        DeviceOrientation.portraitUp,
        DeviceOrientation.portraitDown,
      ]);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final manifest = _manifest;
    final svg = _svgContent;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: Icon(_isLandscape ? Icons.screen_lock_portrait : Icons.screen_lock_landscape),
            tooltip: 'Ekranı Döndür',
            onPressed: _toggleRotation,
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
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _loadError != null || manifest == null || svg == null
              ? Center(child: Text('Harita yüklenemedi: ${_loadError ?? "Bilinmeyen hata"}'))
              : EAEVectorCanvasWidget(
                  manifest: manifest,
                  svgContent: svg,
                  enableMultiSelect: _enableMultiSelect,
                ),
    );
  }
}
